module info.shaclsql.jstimer {
    requires org.apache.jena.core;
    requires org.apache.jena.arq;
    requires org.apache.jena.shacl;
    requires shacl;
    requires org.apache.jena.tdb;


    opens info.shaclsql.jstimer to javafx.fxml;
    exports info.shaclsql.jstimer;
}