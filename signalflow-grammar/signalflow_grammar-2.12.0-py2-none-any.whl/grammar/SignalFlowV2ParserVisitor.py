# Generated from grammar/SignalFlowV2Parser.g4 by ANTLR 4.5.2
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by SignalFlowV2Parser.

class SignalFlowV2ParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by SignalFlowV2Parser#program.
    def visitProgram(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#eval_input.
    def visitEval_input(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#decorator.
    def visitDecorator(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#decorators.
    def visitDecorators(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#decorated.
    def visitDecorated(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#function_definition.
    def visitFunction_definition(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#parameters.
    def visitParameters(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#var_args_list.
    def visitVar_args_list(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#var_args_star_param.
    def visitVar_args_star_param(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#var_args_kws_param.
    def visitVar_args_kws_param(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#var_args_list_param_def.
    def visitVar_args_list_param_def(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#var_args_list_param_name.
    def visitVar_args_list_param_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#statement.
    def visitStatement(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#simple_statement.
    def visitSimple_statement(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#small_statement.
    def visitSmall_statement(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#expr_statement.
    def visitExpr_statement(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#id_list.
    def visitId_list(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#import_statement.
    def visitImport_statement(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#import_name.
    def visitImport_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#import_from.
    def visitImport_from(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#import_as_name.
    def visitImport_as_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#dotted_as_name.
    def visitDotted_as_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#import_as_names.
    def visitImport_as_names(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#dotted_as_names.
    def visitDotted_as_names(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#dotted_name.
    def visitDotted_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#return_statement.
    def visitReturn_statement(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#flow_statement.
    def visitFlow_statement(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#compound_statement.
    def visitCompound_statement(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#assert_statement.
    def visitAssert_statement(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#if_statement.
    def visitIf_statement(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#suite.
    def visitSuite(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#test.
    def visitTest(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#testlist_nocond.
    def visitTestlist_nocond(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#test_nocond.
    def visitTest_nocond(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#lambdef.
    def visitLambdef(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#lambdef_nocond.
    def visitLambdef_nocond(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#or_test.
    def visitOr_test(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#and_test.
    def visitAnd_test(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#not_test.
    def visitNot_test(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#comparison.
    def visitComparison(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#expr.
    def visitExpr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#xor_expr.
    def visitXor_expr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#and_expr.
    def visitAnd_expr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#shift_expr.
    def visitShift_expr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#arith_expr.
    def visitArith_expr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#term.
    def visitTerm(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#factor.
    def visitFactor(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#power.
    def visitPower(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#atom_expr.
    def visitAtom_expr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#atom.
    def visitAtom(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#trailer.
    def visitTrailer(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#subscript.
    def visitSubscript(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#list_expr.
    def visitList_expr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#list_maker.
    def visitList_maker(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#tuple_expr.
    def visitTuple_expr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#dict_expr.
    def visitDict_expr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#testlist_comp.
    def visitTestlist_comp(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#testlist.
    def visitTestlist(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#actual_args.
    def visitActual_args(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#actual_star_arg.
    def visitActual_star_arg(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#actual_kws_arg.
    def visitActual_kws_arg(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#argument.
    def visitArgument(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#list_iter.
    def visitList_iter(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#list_for.
    def visitList_for(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#list_if.
    def visitList_if(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#comp_iter.
    def visitComp_iter(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#comp_for.
    def visitComp_for(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SignalFlowV2Parser#comp_if.
    def visitComp_if(self, ctx):
        return self.visitChildren(ctx)


