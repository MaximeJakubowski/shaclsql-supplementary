from typing import List

from rdflib import Literal, URIRef, BNode, RDF, XSD

from slsparser.shapels import SANode, Op
from slsparser.pathls import PANode, POp

"""
OTHER SPECIALIZED QUERY IDEAS:

- FORALL E. CONSTANT 
"""


def _get_top() -> str:
    return "SELECT Node FROM Nodes"

def _get_and(subqueries: List[str]) -> str:
    res = ""
    for query in subqueries:
        res += f"({query}) INTERSECT "
    return res[:-11]

def _get_or(subqueries: List[str]) -> str:
    res = ""
    for query in subqueries:
        res += f"({query}) UNION "
    return res[:-7]

def _get_eq_pq(pred_p: PANode, pred_q: PANode) -> str:
    p_iri = pred_p.children[0] #overwritten if inverse
    q_iri = pred_q.children[0]

    p_inv = pred_p.pop == POp.INV
    if p_inv:
        p_iri = pred_p.children[0].children[0]

    return f"""
        SELECT Node FROM Nodes WHERE NOT EXISTS (
            ((  SELECT {"Object" if not p_inv else "Subject"}
                FROM Triples
                WHERE Predicate = '{p_iri}'
                    AND {"Subject" if not p_inv else "Object"} = Node
             ) EXCEPT (
                SELECT Object
                FROM Triples
                WHERE Predicate = '{q_iri}'
                    AND Subject = Node
             )) UNION ((
                SELECT Object
                FROM Triples
                WHERE Predicate = '{q_iri}'
                    AND Subject = Node
             ) EXCEPT (
                SELECT {"Object" if not p_inv else "Subject"}
                FROM Triples
                WHERE Predicate = '{p_iri}'
                    AND {"Subject" if not p_inv else "Object"} = Node )))
        """


def _get_eq_id(pred: PANode) -> str:
    return f"""
        SELECT Subject AS Node 
        FROM Triples AS T1 
        WHERE Predicate = '{pred.children[0]}'
            AND Subject = Object
            AND NOT EXISTS (
                SELECT *
                FROM Triples AS T2 WHERE Predicate = '{pred.children[0]}'
                    AND T2.Subject = T1.Subject
                    AND T2.Object <> T1.Object )
        """


def _get_disj_pq(pred_p: PANode, pred_q: PANode) -> str:
    return f"SELECT Node FROM Nodes EXCEPT ({_get_neg_disj_pq(pred_p, pred_q)})"


def _get_disj_id(pred: PANode) -> str:
    return f"SELECT Node FROM Nodes EXCEPT ({_get_neg_disj_id(pred)})"


def _get_closed(preds: List[PANode]) -> str:
    return f"SELECT Node FROM Nodes EXCEPT ({_get_neg_closed(preds)})"


def _get_lessthan(pred_p: PANode, pred_q: PANode, eq=False) -> str:
    p_iri = pred_p.children[0] #overwritten if inverse
    q_iri = pred_q.children[0]

    p_inv = pred_p.pop == POp.INV
    if p_inv:
        p_iri = pred_p.children[0].children[0]

    return f"""
        SELECT Node FROM Nodes WHERE (
            SELECT MAX(N.Value)
            FROM Triples AS T, Numerics AS N
            WHERE T.{"Subject" if not p_inv else "Object"} = Nodes.Node
                AND T.Predicate = '{p_iri}'
                AND T.{"Object" if not p_inv else "Subject"} = N.Node 
                ) {'<' if not eq else '<='} (
            SELECT MIN(N.Value)
            FROM Triples AS T, Numerics AS N
            WHERE T.Subject = Nodes.Node
                AND T.Predicate = '{q_iri}'
                AND T.Object = N.Node )
    """

def _get_lessthaneq(pred_p: PANode, pred_q: PANode) -> str:
    return _get_lessthan(pred_p, pred_q, eq=True)


def _get_uniquelang(pred: PANode) -> str:
    p_iri = pred.children[0] #overwritten if inverse
    p_inv = pred.pop == POp.INV
    if p_inv:
        p_iri = pred.children[0].children[0]

    return f"""
      SELECT Node FROM Nodes WHERE NOT EXISTS (
            SELECT L.Lang
            FROM Triples AS T, Literals AS L
            WHERE T.{"Subject" if not p_inv else "Object"} = Nodes.Node
                AND T.Predicate = '{p_iri}'
                AND T.{"Object" if not p_inv else "Subject"} = L.Node 
                AND L.Lang IS NOT NULL 
                GROUP BY L.Lang 
                HAVING COUNT(*) > 1 )
    """


def _get_countrange(lower: int, upper: int | None, pred: PANode, subquery: str, top=False) -> str:
    p_iri = pred.children[0] #overwritten if inverse
    p_inv = pred.pop == POp.INV
    if p_inv:
        p_iri = pred.children[0].children[0]

    # in this case, it is simply TOP
    if lower == 0 and upper is None:
        return _get_top()
    
    # otherwise, it is a (qualified) maxcount
    if lower == 0 and upper is not None:
        return f"""
        SELECT Node FROM Nodes 
        WHERE Node NOT IN ({_get_countrange(upper + 1, None, pred, subquery, top=top)})
        """
    
    # group clause depends on upper and lower bound
    group_clause = "" if upper is None and lower == 1 else f""" 
        GROUP BY {"Subject" if not p_inv else "Object"}
        HAVING COUNT(*) >= {lower} {f"AND COUNT(*) <= {upper}" if upper is not None else ""}""" 

    # but if they are equal, we can just as well write:
    if lower == upper:
        group_clause = f"""
            GROUP BY {"Subject" if not p_inv else "Object"}
            HAVING COUNT(*) = {lower}
        """

    # if subquery is top, we simplify further
    return f"""
        SELECT {"Subject" if not p_inv else "Object"} AS Node
        FROM Triples{f", ({subquery}) AS Q(Node)" if not top else ""}
        WHERE Predicate = '{p_iri}'
            {f"AND {'Object' if not p_inv else 'Subject'} = Q.Node" if not top else ""}
            {group_clause}
        """
    
def _get_forall(pred: PANode, subquery: str) -> str:
    p_iri = pred.children[0] #overwritten if inverse
    p_inv = pred.pop == POp.INV
    if p_inv:
        p_iri = pred.children[0].children[0]

    return f"""
        SELECT Node FROM Nodes WHERE NOT EXISTS (
            SELECT *
            FROM Triples
            WHERE Predicate = '{p_iri}'
                AND {"Subject" if not p_inv else "Object"} = Node
                AND {"Object" if not p_inv else "Subject"} NOT IN ({subquery}) )
    """


def _get_hasvalue(term: URIRef | BNode | Literal) -> str:
    if isinstance(term, URIRef):
        return f"""
        SELECT Node FROM IRIs 
        WHERE Value = '{term}' """ 
    
    if isinstance(term, BNode):
        return f"""
        SELECT Node FROM Blanks 
        WHERE Alias = '{term}'
        """
    
    if isinstance(term, Literal):
        datatypeval = __sparql_datatype(term)
        return f"""
            SELECT Node
            FROM Literals
            WHERE Value = '{__escape_singlequote(str(term))}'
                AND Type {f"= '{datatypeval}'" if datatypeval is not None else "IS NULL"}
                AND Lang {f"= '{term.language}'" if term.language is not None else " IS NULL"}
        """

def _get_test_nodekind_iri() -> str:
    return "SELECT Node FROM IRIs"


def _get_test_nodekind_blank() -> str:
    return "SELECT Node FROM Blanks"


def _get_test_nodekind_literal() -> str:
    return "SELECT Node FROM Literals"


def _get_test_datatype(d: URIRef) -> str:
    return f"""
    SELECT Node FROM Literals
    WHERE Type = '{d}'
    """


def _get_test_numeric_range(min: float | None, minincl: bool, max: float | None, maxincl: bool) -> str:
    if min is None and max is None:
        raise ValueError("Both min and max are None!")
    
    return f"""
    SELECT Node FROM Numerics
    WHERE 
        {f'Value {">=" if minincl else ">"} {min}' if min is not None else ''}
        {" AND " if min is not None and max is not None else ""}
        {f'Value {"<=" if maxincl else "<"} {max}' if max is not None else ''}
    """


def _get_test_length_range(min: int | None, max: int | None) -> str:
    return f"""
    (SELECT Node FROM Literals 
    WHERE 
        {f"length(Value) >= {min}" if min is not None else ""}
        {f" AND " if min is not None and max is not None else ""}
        {f"length(Value) <= {max}" if max is not None else ""})
    UNION
    (SELECT Node FROM IRIs 
    WHERE 
        {f"length(Value) >= {min}" if min is not None else ""}
        {f" AND " if min is not None and max is not None else ""}
        {f"length(Value) <= {max}" if max is not None else ""})
    """


def _get_test_pattern(pattern: str, flags: str) -> str:
    # TODO: flags
    return f"""
    (SELECT Node FROM Literals
    WHERE regexp_matches(Value, '{pattern}'{f", '{flags[0]}'" if len(flags) > 0 else ''}) )
    UNION
    (SELECT Node FROM IRIs
    WHERE regexp_matches(Value, '{pattern}'{f", '{flags[0]}'" if len(flags) > 0 else ''}) )
    """


def _get_test_languagein(langs: List[str]) -> str:
    langliststr = ""
    for lang in langs:
        langliststr += f""" '{lang}',"""
    langliststr = langliststr[:-1] #remove comma

    return f"""
    SELECT Node FROM Literals
    WHERE Lang IN ({langliststr})
    """


def _get_bot():
    return "SELECT Node FROM Nodes WHERE false"


def _get_neg_eq_pq(pred_p: PANode, pred_q: PANode) -> str:
    p_iri = pred_p.children[0] #overwritten if inverse
    q_iri = pred_q.children[0]

    p_inv = pred_p.pop == POp.INV
    if p_inv:
        p_iri = pred_p.children[0].children[0]

    return f"""
    SELECT Node FROM Nodes WHERE EXISTS (( 
        SELECT * FROM Triples
        WHERE Predicate = '{p_iri}'
            AND {"Object" if not p_inv else "Subject"} NOT IN (
                SELECT Object From Triples 
                WHERE Subject = Node
                    AND Predicate = '{q_iri}' )
        ) UNION (
        SELECT * FROM Triples 
        WHERE Predicate = '{q_iri}'
            AND Object NOT IN (
                SELECT {"Object" if not p_inv else "Subject"} From Triples
                WHERE {"Subject" if not p_inv else "Object"} = Node
                    AND Predicate = '{p_iri}' )))
    """


def _get_neg_eq_id(pred: PANode) -> str:
    return f"""
        SELECT Node FROM Nodes
        WHERE Node NOT IN (
            SELECT * FROM Triples
            WHERE Subject = Node
                AND Predicate = '{pred.children[0]}'
            ) OR EXISTS (
            SELECT * FROM Triples 
            WHERE Predicate = '{pred.children[0]}'
                AND Object <> Node )
        """


def _get_neg_disj_pq(pred_p: PANode, pred_q: PANode) -> str:
    p_iri = pred_p.children[0] #overwritten if inverse
    q_iri = pred_q.children[0]

    p_inv = pred_p.pop == POp.INV
    if p_inv:
        p_iri = pred_p.children[0].children[0]

    return f"""
        SELECT T1.{"Subject" if not p_inv else "Object"} AS Node
        FROM Triples AS T1, Triples AS T2
        WHERE T1.{"Subject" if not p_inv else "Object"} = T2.Subject
            AND T1.Predicate = '{p_iri}'
            AND T2.Predicate = '{q_iri}'
            AND T1.{"Object" if not p_inv else "Subject"} = T2.Object
    """


def _get_neg_disj_id(pred: PANode) -> str:
    return f"""
        SELECT Subject AS NODE
        FROM Triples
        WHERE Predicate = '{pred.children[0]}'
              AND Subject = Object
    """


def _get_neg_closed(preds: List[PANode]) -> str:
    predliststr = ""
    for pred in preds:
        predliststr += f""" '{pred.children[0]}',"""
    predliststr = predliststr[:-1] #remove comma

    return f"""
        SELECT Subject AS Node
        FROM Triples
        WHERE Predicate NOT IN ({predliststr}) 
    """


def _get_neg_lessthan(pred_p: PANode, pred_q: PANode, eq=False) -> str:
    p_iri = pred_p.children[0] #overwritten if inverse
    q_iri = pred_q.children[0]

    p_inv = pred_p.pop == POp.INV
    if p_inv:
        p_iri = pred_p.children[0].children[0]
    
    return f"""
        SELECT T1.Subject AS Node
        FROM Triples AS T1, Triples AS T2,
            Numerics AS N1, Numerics AS N2 
        WHERE T1.Predicate = '{p_iri}'
            AND T2.Predicate = '{q_iri}'
            AND T1.{"Object" if not p_inv else "Subject"} = N1.Node 
            AND T2.Object = N2.Node 
            AND N1.Value {'>=' if not eq else '>'} N2.Value
    """

def _get_neg_lessthaneq(pred_p: PANode, pred_q: PANode) -> str:
    return _get_neg_lessthan(pred_p, pred_q, eq=True)


def _get_neg_uniquelang(pred: PANode) -> str:
    p_iri = pred.children[0] #overwritten if inverse
    p_inv = pred.pop == POp.INV
    if p_inv:
        p_iri = pred.children[0].children[0]

    return f"""
        SELECT Subject AS Node
        FROM Triples AS T1, Tripples AS T2,
            Literals AS L1, Literals AS L2
        WHERE T1.{"Subject" if not p_inv else "Object"} = T2.{"Subject" if not p_inv else "Object"}
            AND T1.Predicate = '{p_iri}'
            AND T2.Predicate = '{p_iri}'
            AND T1.{"Object" if not p_inv else "Subject"} = L1.Node 
            AND T2.{"Object" if not p_inv else "Subject"} = L2.Node 
            AND L1.Lang <> L2.Lang
    """


def _get_neg_hasvalue(term: URIRef | BNode | Literal) -> str:
    if isinstance(term, URIRef):
        return f"""
            SELECT Node FROM Literals
            UNION
            SELECT Node FROM Blanks
            UNION
            SELECT Node FROM IRIs WHERE Value <> '{term}'
        """

    if isinstance(term, BNode):
        return f"""
            SELECT Node FROM Literals
            UNION
            SELECT Node FROM IRIs
            UNION
            SELECT Node FROM Blanks 
            WHERE Alias <> '{term}'
        """

    if isinstance(term, Literal):
        datatypeval = __sparql_datatype(term)
        return f"""
            SELECT Node FROM IRIs
            UNION
            SELECT Node FROM Blanks
            UNION
            SELECT Node FROM Literals 
            WHERE Value <> '{__escape_singlequote(str(term))}'
                OR Type {f"<> '{datatypeval}'" if datatypeval is not None else "IS NOT NULL"}
                {"OR Lang IS NOT NULL" if term.language is None else 
                f"OR Lang <> '{term.language}'"}
        """


def _get_neg_test_nodekind_iri() -> str:
    return """
    SELECT Node FROM Blanks
    UNION
    SELECT Node FROM Literals
    """

def _get_neg_test_nodekind_blank() -> str:
    return """
    SELECT Node FROM IRIs
    UNION
    SELECT Node FROM Literals
    """

def _get_neg_test_nodekind_literal() -> str:
    return """
    SELECT Node FROM Blanks
    UNION
    SELECT Node FROM IRIs
    """


def _get_neg_test_datatype(d: URIRef) -> str:
    return f"""
        SELECT Node FROM IRIs
        UNION
        SELECT Node FROM Blanks
        UNION
        SELECT Node FROM Literals 
        WHERE Type <> '{d}'
    """


def _get_neg_test_numeric_range(min: float | None, minincl: bool, max: float | None, maxincl: bool) -> str:
    if min is None and max is None:
        raise ValueError("Both min and max are None!")
    
    return f"""
        SELECT Node FROM IRIs
        UNION
        SELECT Node FROM Blanks
        UNION (
            SELECT Node FROM Literals 
            EXCEPT (
            SELECT Node FROM Numerics
            WHERE 
            {f'Value {"<=" if minincl else "<"} {min}' if min is not None else ''}
            {" AND " if min is not None and max is not None else ""}
            {f'Value {">=" if maxincl else ">"} {max}' if max is not None else ''} )
    """


def _get_neg_test_length_range(min: int | None, max: int | None) -> str:
    return f"""
        SELECT Node FROM Blanks
        UNION
        (SELECT Node FROM Literals 
        WHERE 
            {f"length(Value) < {min}" if min is not None else ""}
            {f" AND " if min is not None and max is not None else ""}
            {f"length(Value) > {max}" if max is not None else ""})
        UNION
        (SELECT Node FROM IRIs 
        WHERE 
            {f"length(Value) < {min}" if min is not None else ""}
            {f" AND " if min is not None and max is not None else ""}
            {f"length(Value) > {max}" if max is not None else ""})
    """


def _get_neg_test_pattern(pattern: str, flags: str) -> str:
    # TODO: flags
    return f"""
        SELECT Node FROM Blanks
        UNION
        (SELECT Node FROM Literals
        WHERE NOT regexp_matches(Value, '{pattern}'{f", '{flags[0]}'" if len(flags) > 0 else ''}) )
        UNION
        (SELECT Node FROM IRIs
        WHERE NOT regexp_matches(Value, '{pattern}'{f", '{flags[0]}'" if len(flags) > 0 else ''}) )
    """


def _get_neg_test_languagein(langs: List[str]) -> str:
    langliststr = ""
    for lang in langs:
        langliststr += f""" '{lang}',"""
    langliststr = langliststr[:-1] #remove comma

    return f"""
        SELECT Node FROM IRIs
        UNION
        SELECT Node FROM Blanks
        UNION
        SELECT Node FROM Literals
        WHERE Lang NOT IN ({langliststr})
            OR Lang IS NULL
    """

def __escape_singlequote(value):
    out = ""
    for char in value:
        if char == "'":
            out += "''"
        else:
            out += char
    return out

def __sparql_datatype(term: Literal):
    if term.language:
        return RDF.langString
    elif not term.datatype and not term.language:
        return XSD.string
        
    return term.datatype
