package info.shaclsql.jstimer;

import org.apache.jena.graph.Graph;
import org.apache.jena.graph.Node;
import org.apache.jena.graph.NodeFactory;
import org.apache.jena.graph.Triple;
import org.apache.jena.query.Dataset;
import org.apache.jena.rdf.model.*;
import org.apache.jena.riot.Lang;
import org.apache.jena.riot.RDFDataMgr;
import org.apache.jena.riot.RiotNotFoundException;
import org.apache.jena.shacl.ShaclValidator;
import org.apache.jena.shacl.Shapes;
import org.apache.jena.shacl.ValidationReport;
import org.apache.jena.util.FileUtils;
import org.topbraid.shacl.validation.ValidationUtil;
import org.apache.jena.tdb.TDBFactory;
import org.apache.jena.vocabulary.RDF;

import org.topbraid.jenax.util.JenaUtil;

import java.util.ArrayList;
import java.util.List;

import static org.apache.jena.vocabulary.RDF.*;

public class JSTimer {
    public static List<Triple> toremtrip;
    public static List<Statement> toremstat;

    public static void main(String[] args) {
        if (args.length != 5) {
            System.err.println("Invalid number of arguments.");
            System.err.println("jstimer MODE TYPE MEM SHAPEFILE DATA(FILE)(TDB)");
            System.err.println("where MODE is -v (simply validate) -r (retrieve trick)");
            System.err.println("where TYPE is -j (jena) or -t (topq)");
            System.err.println("where MEM is -m (memory) -t (tdb)");
            return;
        }

        String MODE = args[0];
        String TYPE = args[1];
        String MEM = args[2];
        String SHAPES = args[3];
        String DATA = args[4];

        if (TYPE.equals("-j")) {
            timeJena(MODE, MEM, SHAPES, DATA);
        } else if (TYPE.equals("-t")) {
            timeTQ(MODE, MEM, SHAPES, DATA);
        } else {
            System.err.println("Option unknown");
        }
    }

    public static Model getDataModel(String MODE, String MEM, String DATA) throws Exception {
        Model dataModel;

        if (MEM.equals("-m")) {
            dataModel = JenaUtil.createMemoryModel();
            dataModel.read(DATA, FileUtils.langTurtle);
        } else if (MEM.equals("-t")) {
            Dataset dataset = TDBFactory.createDataset(DATA);
            dataModel = dataset.getDefaultModel();
        } else {
            throw new Exception("Error: unknown MEM");
        }

        List<Statement> hackStatements = new ArrayList<Statement>();
        if (MODE.equals("-r")) {
            //System.out.println("DEBUG: before size " + dataModel.size());
            // Iterate through all statements in the model
            StmtIterator stmtIterator = dataModel.listStatements();
            while (stmtIterator.hasNext()) {
                Statement statement = stmtIterator.nextStatement();
                Resource subject = statement.getSubject();

                RDFNode dummy = dataModel.createResource("http://example.org/shaclsql/Dummy");
                Statement toadd = dataModel.createStatement(subject, RDF.type, dummy);
                hackStatements.add(toadd);
            }
            dataModel.add(hackStatements);
            //System.out.println("DEBUG: after size " + dataModel.size());
            toremstat = hackStatements;
        }
        return dataModel;
    }

    public static void timeTQ(String MODE, String MEM, String SHAPES, String DATA) {
        // Load the data
        // Load the RDF data into a Jena Model
        Model dataModel;
        try {
            dataModel = getDataModel(MODE, MEM, DATA);
        } catch (Exception e) {
            System.err.print("Data graph error: ");
            System.err.println(DATA);
            System.err.println(e);
            return;
        }

        // Load the shape
        Model shapeModel;
        //shapeModel.read(JSTimer.class.getResourceAsStream(SHAPES), "urn:dummy", FileUtils.langTurtle);
        try {
            shapeModel = JenaUtil.createMemoryModel();
            shapeModel.read(SHAPES, FileUtils.langTurtle);
        } catch (Exception e) {
            System.err.print("Shapes graph file not found: ");
            System.err.println(SHAPES);
            return;
        }

        // Perform the validation and time
        long startTime = System.currentTimeMillis();
        Resource report = ValidationUtil.validateModel(dataModel, shapeModel, true);
        long endTime = System.currentTimeMillis();
        System.out.print(endTime - startTime);

        if (MODE.equals("-r")) {
            for (Statement statement : toremstat) {
                dataModel.remove(statement);
            }
        }

        dataModel.close();
    }

    public static Graph getDataGraph(String MODE, String MEM, String DATA) throws Exception {
        Graph dataGraph;

        if (MEM.equals("-m")) {
            dataGraph = RDFDataMgr.loadGraph(DATA);
        } else if (MEM.equals("-t")) {
            Dataset dataset = TDBFactory.createDataset(DATA);
            dataGraph = dataset.asDatasetGraph().getDefaultGraph();
        } else {
            throw new Exception("Error: unknown MEM");
        }

        List<Triple> hackStatements = new ArrayList<Triple>();
        if (MODE.equals("-r")) {
            //System.out.println("DEBUG: before size " + dataGraph.size());
            dataGraph.find(Node.ANY, Node.ANY, Node.ANY).forEachRemaining(triple -> {
                // Add the subject to the set
                //System.err.println("DEBUG: getting...");
                Node subject = triple.getSubject();
                //System.err.println("DEBUG: making..." + subject);
                Node predicate = NodeFactory.createURI("http://www.w3.org/1999/02/22-rdf-syntax-ns#type");
                Node dummy = NodeFactory.createURI("http://example.org/shaclsql/Dummy");
                //System.err.println("DEBUG: making..." + predicate);
                //System.err.println("DEBUG: making..." + dummy);
                hackStatements.add(Triple.create(subject, predicate, dummy));
                //System.err.println("DEBUG: finish one");
            });

            //System.err.println("DEBUG: Adding...");
            for (Triple triple: hackStatements) {
                dataGraph.add(triple);
            }
            toremtrip = hackStatements;
            //System.out.println("DEBUG: after size " + dataGraph.size());
        }

        return dataGraph;
    }

    public static void timeJena(String MODE, String MEM, String SHAPES, String DATA) {
        Graph dataGraph;
        try {
            dataGraph = getDataGraph(MODE, MEM, DATA);
        } catch (Exception e) {
            System.err.print("Data graph error: ");
            System.err.println(DATA);
            System.err.print(e);
            return;
        }

        Graph shapesGraph;
        try {
            shapesGraph = RDFDataMgr.loadGraph(SHAPES);
        } catch (RiotNotFoundException e) {
            System.err.print("Shapes graph file not found: ");
            System.err.println(SHAPES);
            return;
        }

        Shapes shapes;
        try {
            shapes = Shapes.parse(shapesGraph);
        } catch (Exception e) {
            System.err.println("Cannot parse shapesgraph.");
            return;
        }

        long startTime = System.currentTimeMillis();
        ValidationReport report = ShaclValidator.get().validate(shapes, dataGraph);
        long endTime = System.currentTimeMillis();
        //System.out.println("DEBUG SIZE: " + report.getEntries().size());
        System.out.print(endTime - startTime);

        if (MODE.equals("-r")) {
            for (Triple triple : toremtrip) {
                dataGraph.remove(triple.getSubject(), triple.getPredicate(), triple.getObject());
            }
        }

        dataGraph.close();
    }
}