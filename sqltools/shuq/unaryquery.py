from typing import List, Dict

from rdflib import Literal, URIRef, BNode, SH, IdentifiedNode, RDF

from slsparser.shapels import SANode, Op
from slsparser.pathls import PANode, POp
from slsparser.utilities import expand_shape, negation_normal_form

import shuq.querylib as ql

def translate_node(node: SANode, negated=False) -> str:
    """
    We assume the node is expanded and in negation normal form
    """
    if node.op == Op.TOP:
        return ql._get_top()
    
    if node.op == Op.BOT:
        return ql._get_bot()
    
    if node.op == Op.EQ and node.children[0].pop != POp.ID:
        pred_p = node.children[0]
        pred_q = node.children[1]
        return ql._get_eq_pq(pred_p, pred_q)
    
    if node.op == Op.EQ and node.children[0].pop == POp.ID:
        pred = node.children[1]
        return ql._get_eq_id(pred)
    
    if node.op == Op.DISJ and node.children[0].pop != POp.ID:
        pred_p = node.children[0]
        pred_q = node.children[1]
        return ql._get_disj_pq(pred_p, pred_q)
    
    if node.op == Op.DISJ and node.children[0].pop == POp.ID:
        pred = node.children[1]
        return ql._get_disj_id(pred)
    
    if node.op == Op.CLOSED:
        return ql._get_closed(node.children)
    
    if node.op == Op.LESSTHAN:
        pred_p = node.children[0]
        pred_q = node.children[1]
        return ql._get_lessthan(pred_p, pred_q)
    
    if node.op == Op.LESSTHANEQ:
        pred_p = node.children[0]
        pred_q = node.children[1]
        return ql._get_lessthaneq(pred_p, pred_q)
    
    if node.op == Op.UNIQUELANG:
        pred = node.children[0]
        return ql._get_uniquelang(pred)
    
    if node.op == Op.COUNTRANGE:
        lower = int(node.children[0])
        upper = None if node.children[1] is None else int(node.children[1])
        pred = node.children[2]
        istop = node.children[3].op == Op.TOP
        subquery = ""
        if not istop:
            subquery = translate_node(node.children[3])
        return ql._get_countrange(lower, upper, pred, subquery, top=istop)
    
    if node.op == Op.FORALL:
        pred = node.children[0]
        subquery = translate_node(node.children[1])
        return ql._get_forall(pred, subquery)
    
    if node.op == Op.HASVALUE:
        return ql._get_hasvalue(node.children[0])
    
    if node.op == Op.TEST:
        constraintcomponent = node.children[0]
        if constraintcomponent == SH.NodeKindConstraintComponent:
            nodekind = node.children[1]
            if nodekind == SH.IRI:
                return ql._get_test_nodekind_iri()
            if nodekind == SH.BlankNode:
                return ql._get_test_nodekind_blank()
            if nodekind == SH.Literal:
                return ql._get_test_nodekind_literal()
            if nodekind == SH.IRIOrLiteral:
                return f"""
                {ql._get_test_nodekind_iri()}
                UNION
                {ql._get_test_nodekind_literal()}
                """
            if nodekind == SH.BlankNodeOrIRI:
                return f"""
                {ql._get_test_nodekind_iri()}
                UNION
                {ql._get_test_nodekind_blank()}
                """
            if nodekind == SH.BlankNodeOrLiteral:
                return f"""
                {ql._get_test_nodekind_literal()}
                UNION
                {ql._get_test_nodekind_blank()}
                """
            raise ValueError
        if constraintcomponent == SH.DatatypeConstraintComponent:
            datatype = node.children[1]
            return ql._get_test_datatype(datatype)
        if constraintcomponent == 'numeric_range':
            min = None
            try:
                min_index = node.children.index(SH.MinInclusiveConstraintComponent) + 1
                min = float(node.children[min_index])
            except: 
                try:
                    min_index = node.children.index(SH.MinExclusiveConstraintComponent) + 1
                    min = float(node.children[min_index])
                except: pass
            minincl = SH.MinInclusiveConstraintComponent in node.children
            max = None
            try:
                max_index = node.children.index(SH.MaxInclusiveConstraintComponent) + 1
                max = float(node.children[max_index])
            except: 
                try:
                    max_index = node.children.index(SH.MaxExclusiveConstraintComponent) + 1
                    max = float(node.children[max_index])
                except: pass
            maxincl = SH.MaxInclusiveConstraintComponent in node.children
            return ql._get_test_numeric_range(min, minincl, max, maxincl)
        if constraintcomponent == 'length_range':
            min = None
            try:
                min_index = node.children.index(SH.MinLengthConstraintComponent) + 1
                min = node.children[min_index]
            except: pass
            max = None
            try:
                max_index = node.children.index(SH.MaxLengthConstraintComponent) + 1
                max = node.children[max_index]
            except: pass
            return ql._get_test_length_range(min, max)
        if constraintcomponent == SH.PatternConstraintComponent:
            return ql._get_test_pattern(str(node.children[1]), node.children[2])
        if constraintcomponent == SH.LanguageInConstraintComponent:
            return ql._get_test_languagein(node.children[1])
        
    if node.op == Op.AND:
        subqueries = [translate_node(subnode) for subnode in node.children]
        return ql._get_and(subqueries)

    if node.op == Op.OR:
        subqueries = [translate_node(subnode) for subnode in node.children]
        return ql._get_or(subqueries)

    # OTHERWISE IT IS A NOT
    # THIS IS A QUICK AND DIRTY IMPLEMENTATION
    # TOO MUCH REPEATED CODE FROM ABOVE
    # TODO: MAKE MORE GENERAL
    if node.op != Op.NOT:
        raise NotImplementedError(f"SA Operation {str(node.op)} not implemented")

    if node.op == Op.NOT:
        node = node.children[0]

    if node.op == Op.TOP:
        return ql._get_bot()
    
    if node.op == Op.EQ and node.children[0].pop != POp.ID:
        pred_p = node.children[0]
        pred_q = node.children[1]
        return ql._get_neg_eq_pq(pred_p, pred_q)
    
    if node.op == Op.EQ and node.children[0].pop == POp.ID:
        pred = node.children[1]
        return ql._get_neg_eq_id(pred)
    
    if node.op == Op.DISJ and node.children[0].pop != POp.ID:
        pred_p = node.children[0]
        pred_q = node.children[1]
        return ql._get_neg_disj_pq(pred_p, pred_q)
    
    if node.op == Op.DISJ and node.children[0].pop == POp.ID:
        pred = node.children[1]
        return ql._get_neg_disj_id(pred)
    
    if node.op == Op.CLOSED:
        return ql._get_neg_closed(node.children)
    
    if node.op == Op.LESSTHAN:
        pred_p = node.children[0]
        pred_q = node.children[1]
        return ql._get_neg_lessthan(pred_p, pred_q)
    
    if node.op == Op.LESSTHANEQ:
        pred_p = node.children[0]
        pred_q = node.children[1]
        return ql._get_neg_lessthaneq(pred_p, pred_q)
    
    if node.op == Op.UNIQUELANG:
        pred = node.children[0]
        return ql._get_neg_uniquelang(pred)
    
    if node.op == Op.HASVALUE:
        return ql._get_neg_hasvalue(node.children[0])
    
    if node.op == Op.TEST:
        constraintcomponent = node.children[0]
        if constraintcomponent == SH.NodeKindConstraintComponent:
            nodekind = node.children[1]
            if nodekind == SH.IRI:
                return ql._get_neg_test_nodekind_iri()
            if nodekind == SH.BlankNode:
                return ql._get_neg_test_nodekind_blank()
            if nodekind == SH.Literal:
                return ql._get_neg_test_nodekind_literal()
            if nodekind == SH.IRIOrLiteral:
                return f"""
                {ql._get_neg_test_nodekind_iri()}
                UNION
                {ql._get_neg_test_nodekind_literal()}
                """
            if nodekind == SH.BlankNodeOrIRI:
                return f"""
                {ql._get_neg_test_nodekind_iri()}
                UNION
                {ql._get_neg_test_nodekind_blank()}
                """
            if nodekind == SH.BlankNodeOrLiteral:
                return f"""
                {ql._get_neg_test_nodekind_literal()}
                UNION
                {ql._get_neg_test_nodekind_blank()}
                """
            raise ValueError
        if constraintcomponent == SH.DatatypeConstraintComponent:
            datatype = node.children[1]
            return ql._get_neg_test_datatype(datatype)
        if constraintcomponent == 'numeric_range':
            min = None
            try:
                min_index = node.children.index(SH.MinInclusiveConstraintComponent) + 1
                min = float(node.children[min_index])
            except: 
                try:
                    min_index = node.children.index(SH.MinExclusiveConstraintComponent) + 1
                    min = float(node.children[min_index])
                except: pass
            minincl = SH.MinInclusiveConstraintComponent in node.children
            max = None
            try:
                max_index = node.children.index(SH.MaxInclusiveConstraintComponent) + 1
                max = float(node.children[max_index])
            except: 
                try:
                    max_index = node.children.index(SH.MaxExclusiveConstraintComponent) + 1
                    max = float(node.children[max_index])
                except: pass
            maxincl = SH.MaxInclusiveConstraintComponent in node.children
            return ql._get_neg_test_numeric_range(min, minincl, max, maxincl)
        if constraintcomponent == 'length_range':
            min = None
            try:
                min_index = node.children.index(SH.MinLengthConstraintComponent) + 1
                min = node.children[min_index]
            except: pass
            max = None
            try:
                max_index = node.children.index(SH.MaxLengthConstraintComponent) + 1
                max = node.children[max_index]
            except: pass
            return ql._get_neg_test_length_range(min, max)
        if constraintcomponent == SH.PatternConstraintComponent:
            return ql._get_neg_test_pattern(str(node.children[1]), node.children[2])
        if constraintcomponent == SH.LanguageInConstraintComponent:
            return ql._get_neg_test_languagein(node.children[1])

    

    raise NotImplementedError(f"SA Operation NEGATION {str(node.op)} not implemented")


def translate_conformance_shapes(definitions: Dict[IdentifiedNode, SANode], 
                                 targets: Dict[IdentifiedNode, SANode], target_all=False) -> Dict[IdentifiedNode, str]:
    conformance_sql_total = dict()
    
    for target_shape_name in targets.keys():
        if targets[target_shape_name].op == Op.BOT:
            continue
        target_shape = targets[target_shape_name]
        target_shape = _replace_classconstraint(target_shape)

        target_sql = translate_node(target_shape)
        shape = negation_normal_form(
            expand_shape(definitions, definitions[target_shape_name]))
        
        shape = _replace_classconstraint(shape)
        shape_sql = translate_node(shape)
        
        conformance_sql = f"""
        ({target_sql}) 
        EXCEPT 
        ({shape_sql})
        """

        if target_all:
            conformance_sql = shape_sql # simply retrieve all nodes

        conformance_sql_total[target_shape_name] = conformance_sql
        
    
    return conformance_sql_total


def translate_conformance_all(definitions: Dict[IdentifiedNode, SANode], 
                              targets: Dict[IdentifiedNode, SANode], target_all=False) -> str:
    totalquery = ""
    
    cfs = translate_conformance_shapes(definitions, targets, target_all=target_all)

    for shapename in cfs.keys():
        totalquery += f"({cfs[shapename]}) UNION "

    if len(totalquery) == 0:
        raise ValueError("No shapes to check")

    return totalquery[:-6] 


def _replace_classconstraint(original):
    # TODO: to aggressive (possibly replaces too much, no problem for our usecase)
    if original.op == Op.COUNTRANGE and \
        original.children[2].pop == POp.COMP and \
            original.children[2].children[0].children[0] == RDF.type:
            # replace with simplified
            return SANode(
                Op.COUNTRANGE,
                [original.children[0], original.children[1], 
                 PANode(POp.PROP, [RDF.type]), original.children[3]]
            )
    
    new_children = []

    for child in original.children:
        if isinstance(child, SANode):
            new_children.append(_replace_classconstraint(child))
        else:
            new_children.append(child)

    return SANode(original.op, new_children)