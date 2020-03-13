from nltk.corpus import wordnet
import requests
import json

from ConditionalHandling import *
from LineCategorization import *
from Constants import *
from ControlPanel import *


class predicateSwitcher(object):

    def __init__(self):
        self.graphNumber = 0
        self.DRSGraph = ItemGraph(None)

    # Method to call the appropriate function based on the argument passed in
    def callFunction(self, predicateType, predicateContents):
        # Get the name of the method
        methodName = 'predicate_' + str(predicateType)
        # Get the method itself
        method = getattr(self, methodName, lambda: "Unknown predicate")
        # Call the method and return its output
        method(predicateContents)
        return self.DRSGraph

    def updateDRSGraph(self, newDRSGraph):
        self.DRSGraph = newDRSGraph

    # For object() predicates SHOULD CHECK IF OBJECT WITH GIVEN NAME ALREADY EXISTS!!!  IF SO, FIGURE OUT WHAT ARE
    # THE CONDITIONS FOR THAT TO OCCUR
    def predicate_object(self, predicateContents):
        # Break up elements of object line into variables
        predicateComponents = predicateContents.split(',')
        objReferenceVariable = predicateComponents[0]
        objName = predicateComponents[1]
        # FOLLOWING ONES PROBABLY UNUSED BUT LEAVING COMMENTED OUT SO I HAVE ACCESS EASILY
        # objClass = predicateComponents[2]
        # objUnit = predicateComponents[3]
        objOperator = predicateComponents[4]
        objCount = predicateComponents[5].split(')')[0]
        if self.DRSGraph.FindItemWithValue(objReferenceVariable) is None:
            # Apply appropriate variables to ItemGraph
            objectGraph = ItemGraph(self.graphNumber)
            objectGraph.appendItemValue(objReferenceVariable)
            objectGraph.appendItemRole(objName)
            objectGraph.appendItemOp(objOperator)
            objectGraph.appendItemCount(objCount)

            # Increase the graph number for auto-generation of names
            self.graphNumber = self.graphNumber + 1
            # If a main graph already exists, then add the new graph in to it
            if self.DRSGraph.graph is not None:
                self.DRSGraph.graph = networkx.algorithms.operators.binary.compose(self.DRSGraph.graph,
                                                                                   objectGraph.graph)
            # if no main graph exists, this is the main graph
            else:
                self.DRSGraph.graph = objectGraph.graph
            return True
        else:
            return False

    # For predicate() predicates
    # HOW TO HANDLE SENTENCE SUB-ORDINATION?
    def predicate_predicate(self, predicateContents):
        # Intransitive verbs: (predName, verb, subjectRef)
        # - The SubjectRef Verbed (the man laughed, the target appears)
        # Transitive verbs: (predName, verb, subjectRef, dirObjRef)
        # - The Subjectref Verbed the dirObjRef (the task A has a group of objects H,
        # the subject L remembers the letter I)
        # Ditransitive verbs: (predName, verb, subjRef, dirObjRef, indirObjRef)
        # - The SubjectRef verbed the DirObjRef to the indirObjRef (The professor (S) gave
        # the paper (D) to the student (I))

        consequence = False
        # Check if the line passed in was from a conditional's consequence (used to differentiate "be" as an action
        # or not
        if CONST_CONSEQUENCE_FLAG in predicateContents:
            consequence = True

        # Break up the predicate
        predicateComponents = predicateContents.split(',')
        numberOfComponents = len(predicateComponents)
        # Always have first three components, so only special cases are transitive/ditransitive
        predReferenceVariable = predicateComponents[0]
        predVerb = predicateComponents[1]
        predSubjRef = predicateComponents[2]
        # Different cases (differing number of components)
        if numberOfComponents == 3:
            # intransitive
            predSubjRef = predSubjRef.split(')')[0]
        elif numberOfComponents == 4:
            # Transitive
            predDirObjRef = predicateComponents[3].split(')')[0]
        elif numberOfComponents == 5:
            # Ditransitive - NOT YET IMPLEMENTED
            # predIndirObjRef = predicateComponents[4].split(')')[0]
            pass
        else:
            # invalid
            raise ValueError('Too many components ?')
        # Hardcode be case for specific scenarios

        if predVerb == CONST_PRED_VERB_BE:
            # Check if naming or setting an equivalency
            if CONST_PRED_SUBJ_NAMED in predSubjRef:
                # If so call naming method
                self.DRSGraph = self.nameItem(predSubjRef, predDirObjRef, self.DRSGraph)
            # If not named(XYZ) but still has 4 components
            elif numberOfComponents == 4 and consequence is False:
                self.handle_general_predicate(predSubjRef, predVerb, predReferenceVariable,
                                              numberOfComponents, predDirObjRef)
            # HANDLE ANY OTHER CASES????
            # If only 3 components predicate(X,be,Y)
            elif numberOfComponents == 3:
                self.handle_general_predicate(predSubjRef, predVerb, predReferenceVariable, numberOfComponents)
            # If 4 components and part of a predicate
            elif numberOfComponents == 4 and consequence is True:
                self.handle_general_predicate(predSubjRef, predVerb, predReferenceVariable,
                                              numberOfComponents, predDirObjRef)

        # Hardcode "have" case for composition
        elif predVerb == CONST_PRED_VERB_HAVE:
            if numberOfComponents == 4:
                # Get nodes for both subject and direct object
                subjRefNode = self.DRSGraph.FindItemWithValue(predSubjRef)
                dirObjRefNode = self.DRSGraph.FindItemWithValue(predDirObjRef)
                # If both are nodes in the graph, then the "have" is setting a composition
                if subjRefNode is not None and dirObjRefNode is not None:
                    self.DRSGraph.addCompositionEdges(subjRefNode, dirObjRefNode)
        else:
            if numberOfComponents == 3:
                self.handle_general_predicate(predSubjRef, predVerb, predReferenceVariable, numberOfComponents)
            elif numberOfComponents == 4:
                self.handle_general_predicate(predSubjRef, predVerb, predReferenceVariable,
                                              numberOfComponents, predDirObjRef)

    def handle_general_predicate(self, predSubjRef, predVerb, predReferenceVariable,
                                 numberOfComponents, predDirObjRef=None):
        # Create Action Node
        # TODO: CHECK IF THIS CAN'T BE REWORKED TO AVOID USING THIS
        self.DRSGraph.AppendItemAffordanceAtSpecificNode(predSubjRef, predVerb)
        actionGraph = ActionGraph(self.graphNumber)
        actionGraph.appendActionValue(predReferenceVariable)
        actionGraph.appendActionVerb(predVerb)
        # Increase the graph number for auto-generation of names
        self.graphNumber = self.graphNumber + 1
        # If a main graph already exists, then add the new graph in to it
        if self.DRSGraph.graph is not None:
            self.DRSGraph.graph = networkx.algorithms.operators.binary.compose(self.DRSGraph.graph,
                                                                               actionGraph.graph)
        # if no main graph exists, this is the main graph
        else:
            self.DRSGraph.graph = actionGraph.graph

        # Get subject reference node
        subjRefNode = self.DRSGraph.FindItemWithValue(predSubjRef)
        actionNode = self.DRSGraph.FindItemWithValue(predReferenceVariable)

        # If just one subject "The target appears"
        if numberOfComponents == 3:
            self.DRSGraph.addActionPerformerEdges(subjRefNode, actionNode)
        # If subject and direct object (e.g. "The subject remembers the letter")
        # predSubjRef = "Subject", predDirObjRef = "letter"
        elif numberOfComponents == 4:
            dirObjRefNode = self.DRSGraph.FindItemWithValue(predDirObjRef)
            self.DRSGraph.addActionPerformerEdges(subjRefNode, actionNode)
            self.DRSGraph.addActionTargetEdges(actionNode, dirObjRefNode)

        # TODO TODO TODO TODO
        elif numberOfComponents == 5:
            pass

    # For has_part() predicates
    def predicate_has_part(self, predicateContents):
        # Get predicate items
        predicateComponents = predicateContents.split(',')
        predGroupRef = predicateComponents[0]
        predGroupMember = predicateComponents[1].split(')')[0]
        # Hardcode the new object as being a group
        predGroupDescription = CONST_PRED_GROUP_DESC
        # if Group reference doesn't exist
        groupNode = self.DRSGraph.FindItemWithValue(predGroupRef)
        memberNode = self.DRSGraph.FindItemWithValue(predGroupMember)
        if groupNode is None:
            # Then create that item
            # Apply appropriate variables to ItemGraph
            groupGraph = ItemGraph(self.graphNumber)
            groupGraph.appendItemValue(predGroupRef)
            groupGraph.appendItemRole(predGroupDescription)
            # Get the node for the group
            groupNode = groupGraph.FindItemWithValue(predGroupRef)
            # Increase the graph number for auto-name generation
            self.graphNumber = self.graphNumber + 1
            # Compose the new graph with the existing graph
            # (no scenario of no existing graph because can't start with has_part())
            self.DRSGraph.graph = networkx.algorithms.operators.binary.compose(self.DRSGraph.graph, groupGraph.graph)
        # Add membership edges
        self.DRSGraph.addGroupMembershipEdges(groupNode, memberNode)

    # HANDLE MODIFIERS - PREPOSITION
    # TODO TODO TODO TODO
    def predicate_modifier_pp(self, predicateContents):
        # Find action node of predicate
        # Get predicate items
        predicateComponents = predicateContents.split(',')
        modPPRefID = predicateComponents[0] + CONST_PRED_MOD_TAG
        modPPPrep = predicateComponents[1]
        modPPModifiedVerb = predicateComponents[0]
        modPPTargetObj = predicateComponents[2].split(')')[0]

        # Create Modifier Node
        modGraph = ModifierPPGraph(self.graphNumber)
        modGraph.appendModPPValue(modPPRefID)
        modGraph.appendModPPPrep(modPPPrep)

        # Increase the graph number for auto-generation of names
        self.graphNumber = self.graphNumber + 1

        # If a main graph already exists, then add the new graph in to it
        if self.DRSGraph.graph is not None:
            self.DRSGraph.graph = networkx.algorithms.operators.binary.compose(self.DRSGraph.graph, modGraph.graph)
        # if no main graph exists, this is the main graph
        else:
            self.DRSGraph.graph = modGraph.graph

        # Add verb and object modifier edges
        modNode = self.DRSGraph.FindItemWithValue(modPPRefID)
        verbNode = self.DRSGraph.FindItemWithValue(modPPModifiedVerb)
        objectNode = self.DRSGraph.FindItemWithValue(modPPTargetObj)
        self.DRSGraph.addModifierVerbEdges(modNode, verbNode)
        self.DRSGraph.addModifierObjectEdges(modNode, objectNode)

    # HANDLE MODIFIERS - ADVERB
    def predicate_modifier_adv(self, predicateContents):
        pass

    def predicate_relation(self, predicateContents):

        consequence = False
        # Check if the line passed in was from a conditional's consequence (used to differentiate "be" as an action
        # or not
        if CONST_CONSEQUENCE_FLAG in predicateContents:
            consequence = True

        predicateComponents = predicateContents.split(',')
        relationAttributeNodeRef = predicateComponents[0]
        relationOf = predicateComponents[1]
        relationParentNodeRef = predicateComponents[2].split(')')[0]

        # Create Relation Node
        relationGraph = RelationGraph(self.graphNumber)

        # Increase the graph number for auto-generation of names
        self.graphNumber = self.graphNumber + 1

        # If a main graph already exists, then add the new graph in to it
        if self.DRSGraph.graph is not None:
            self.DRSGraph.graph = networkx.algorithms.operators.binary.compose(self.DRSGraph.graph, relationGraph.graph)
        # if no main graph exists, this is the main graph
        else:
            self.DRSGraph.graph = relationGraph.graph

        # Add relation edges between attribute/parent/relation nodes
        # Get newly created relation node
        relationNode = self.DRSGraph.FindItemWithValue(CONST_RELATION_NODE + str(self.graphNumber - 1))
        attributeNode = self.DRSGraph.FindItemWithValue(relationAttributeNodeRef)
        parentNode = self.DRSGraph.FindItemWithValue(relationParentNodeRef)
        self.DRSGraph.addRelationAttributeEdges(attributeNode, relationNode)
        self.DRSGraph.addRelationParentEdges(parentNode, relationNode)

    # HANDLE PROPERTIES
    # TODO: Handle 4/6 component properties
    # TODO: Handle degrees besides "pos"
    def predicate_property(self, predicateContents):
        # Break up the predicate
        predicateComponents = predicateContents.split(',')
        numberOfComponents = len(predicateComponents)
        # Always have first two components, others distributed based on number of components
        propRefId = predicateComponents[0]
        propAdjective = predicateComponents[1]
        # Different cases (differing number of components)
        if numberOfComponents == 3:
            # Only a primary object
            propDegree = predicateComponents[2].split(')')[0]
        elif numberOfComponents == 4:
            # Primary and secondary object
            propDegree = predicateComponents[2]
            # propSecObj = predicateComponents[3].split(')')[0]
        elif numberOfComponents == 6:
            # Primary, secondary, and tertiary objects
            # propSecObj = predicateComponents[2]
            propDegree = predicateComponents[3]
            # propCompTarget = predicateComponents[4]
            # propTertObj = predicateComponents[5].split(')')[0]
        else:
            # invalid
            raise ValueError('Too many components ?')

        existingNodeWithRefId = self.DRSGraph.FindItemWithValue(propRefId)
        if existingNodeWithRefId is None:
            # Apply appropriate variables to PropertyGraph (operating off same graph number
            # because the number in the name is irrelevant)
            propGraph = PropertyGraph(self.graphNumber)
            propGraph.appendPropValue(propRefId)
            propGraph.appendPropAdj(propAdjective)
            propGraph.appendPropDegree(propDegree)
            # Increase the graph number for auto-generation of names
            self.graphNumber = self.graphNumber + 1
            # If a main graph already exists, then add the new graph in to it
            if self.DRSGraph.graph is not None:
                self.DRSGraph.graph = networkx.algorithms.operators.binary.compose(self.DRSGraph.graph, propGraph.graph)
            # if no main graph exists, this is the main graph
            else:
                self.DRSGraph.graph = propGraph.graph
            return True
        else:
            outEdgesFromNode = self.DRSGraph.graph.out_edges(existingNodeWithRefId, data=True)
            adjectiveNode = None
            for startNode, endNode, edgeValues in outEdgesFromNode:
                # If an edge has the value ItemHasName, then we want to modify the end node
                if edgeValues[CONST_NODE_VALUE_KEY] == CONST_PROP_HAS_ADJECTIVE_EDGE:
                    # Update graph with name
                    adjectiveNode = endNode
            if adjectiveNode is not None:
                # TODO: SEE IF I CAN UPDATE THIS TO NOT USE THIS FUNCTION
                self.DRSGraph.AppendValueAtSpecificNode(adjectiveNode, propAdjective)
            else:
                print("Error - Encountered duplicate reference for property but did not find adjective "
                      "node to append to")
            return True

    # Method used to get the name out of a "named" predicate and associate said name with the appropriate object.
    def nameItem(self, predSubjRef, predDirObjRef, DRSGraph):
        # Get item name out of "named(XYZ)"
        itemName = predSubjRef[predSubjRef.find("(") + 1:predSubjRef.find(")")]
        # Replace the name
        DRSGraph.ReplaceItemNameAtSpecificNode(predDirObjRef, "\"" + itemName + "\"")
        # Return graph
        return DRSGraph


# CURRENTLY OPERATING UNDER ASSUMPTION THAT questions ALWAYS end with the predicate as the final piece.
# This will 100% need revised (probably just check if
# the current line is the final question line and then process the complete question at that point).
class questionSwitcher(object):

    def __init__(self):
        self.graphNumber = 0
        self.DRSGraph = None
        self.nodesWithGivenProperty = []
        self.nodesWithGivenPropertyAntonym = []
        self.subjectNode = None
        self.objectNode = None
        self.itemCount = 0
        self.propertyCount = 0
        self.newToOldRefIDMapping = {}
        self.predicateTrue = None
        self.negationActive = None
        self.verbTargetGap = False

    # Method to call the appropriate function based on the argument passed in
    def callFunction(self, predicateType, predicateContents, DRSGraph):
        # Get the name of the method
        methodName = 'question_' + str(predicateType)
        # Get the method itself
        method = getattr(self, methodName, lambda: "Unknown predicate")
        # Call the method and return its output
        self.DRSGraph = DRSGraph
        method(predicateContents)

    def returnDRSGraph(self):
        return self.DRSGraph

    def question_object(self, predicateContents):
        # Get object information
        predicateComponents = predicateContents.split(',')
        objRefId = predicateComponents[0]
        objRole = predicateComponents[1]
        # objClass = predicateComponents[2]
        # objUnit = predicateComponents[3]
        objOperator = predicateComponents[4]
        objCount = predicateComponents[5].split(')')[0]
        # Get item node in original instruction which this SHOULD correspond to (ignoring name for now)
        DRSEquivalentNode = self.findMatchingItemNode(objRole, objOperator, objCount)
        # If we don't find a node for this item, then we have encountered a lexical gap.

        newNymCount = 0
        if CONTROL_IDENTIFY_LEXICAL is True:
            if DRSEquivalentNode is None:
                print("Lexical gap encountered - a role (" + objRole + ") was introduced which is not currently in the"
                                                                       " system's vocabulary.")
                if CONTROL_RESOLVE_LEXICAL is True:
                    # TODO: Allow user to manually choose yes/no to resolve?
                    while DRSEquivalentNode is None and newNymCount < 3:
                        # No nodes "active"
                        newRole = requestNewTermToNymCheck(objRole)
                        newNymCount = newNymCount + 1
                        DRSEquivalentNode = self.findMatchingItemNode(newRole, objOperator, objCount)
                        if DRSEquivalentNode is not None:
                            print("Lexical gap resolved - a role given (" + newRole + ") was found associated with an"
                                                                                      " item in the knowledge base")
                            DRSEquivalentNameNode = self.findRoleNodeConnectedToItemNode(DRSEquivalentNode)
                            self.DRSGraph.AppendValueAtSpecificNode(DRSEquivalentNameNode, objRole)
        # Replace the reference ID (from APE Webclient) to the equivalent node's reference ID (from the graph)
        if self.DRSGraph.graph.has_node(DRSEquivalentNode):
            DRSNodeRefID = self.DRSGraph.graph.node[DRSEquivalentNode][CONST_NODE_VALUE_KEY]
            self.newToOldRefIDMapping.update({objRefId: DRSNodeRefID})
            self.itemCount = self.itemCount + 1
        else:
            self.newToOldRefIDMapping.update({objRefId: None})
        # WILL NEED TO FIND A WAY TO HANDLE NAME AND ROLE TO GET MORE ACCURATE PICTURE?

    # HANDLE PROPERTIES
    # TODO: Handle 4/6 component properties
    # TODO: Handle degrees besides "pos"
    def question_property(self, predicateContents):
        # Declare lists used later
        adjectiveNodes = []
        antonymNodes = []
        openGap = False
        # Break up the predicate
        predicateComponents = predicateContents.split(',')
        numberOfComponents = len(predicateComponents)
        # Always have first two components, others distributed based on number of components
        propRefId = predicateComponents[0]
        propAdjective = predicateComponents[1]
        # Different cases (differing number of components) - completely unused right now, but leaving commented out
        # in case of implementation
        if numberOfComponents == 3:
            # Only a primary object
            # propDegree = predicateComponents[2].split(')')[0]
            pass
        elif numberOfComponents == 4:
            # Primary and secondary object
            # propDegree = predicateComponents[2]
            # propSecObj = predicateComponents[3].split(')')[0]
            pass
        elif numberOfComponents == 6:
            # Primary, secondary, and tertiary objects
            # propSecObj = predicateComponents[2]
            # propDegree = predicateComponents[3]
            # propCompTarget = predicateComponents[4]
            # propTertObj = predicateComponents[5].split(')')[0]
            pass
        else:
            # invalid
            raise ValueError('Too many components ?')

        # INITIAL NYM TESTING - will need to extend to other predicates as well of course
        # TODO: Resolve occurs before identify here - that shouldn't be the case probably
        adjectiveNymList, antonymList = getNyms(propAdjective)
        if CONTROL_RESOLVE_LEXICAL is True:
            adjectiveNodes = self.ListOfNodesWithValueFromList(adjectiveNymList)
        else:
            adjectiveNodes = self.ListOfNodesWithValue(propAdjective)
        if CONTROL_IDENTIFY_NEGATION is True:
            antonymNodes = self.ListOfNodesWithValueFromList(antonymList)

        newNymCount = 0
        if CONTROL_IDENTIFY_LEXICAL is True:
            if len(adjectiveNodes) < 1:
                openGap = True
                print("Lexical gap encountered - an adjective (" + propAdjective + ") was introduced which is not"
                                                                                   " currently in the system's vocabulary.")
            if CONTROL_RESOLVE_LEXICAL is True:
                # TODO: Allow user to manually choose yes/no to resolve?
                # Should antonymNodes be counted here too?
                while len(adjectiveNodes) < 1 and len(antonymNodes) < 1 and newNymCount < 3:
                    # No nodes "active"
                    newAdjective = requestNewTermToNymCheck(propAdjective)
                    newNymCount = newNymCount + 1
                    adjectiveNymList, newAntonymList = getNyms(newAdjective)
                    antonymNodes = self.ListOfNodesWithValueFromList(newAntonymList)
                    adjectiveNodes = self.ListOfNodesWithValueFromList(adjectiveNymList)
                    if len(adjectiveNodes) > 0:
                        print("Lexical gap resolved - an adjective given (" + newAdjective + ") was found in the"
                                                                                             " knowledge base")

        if len(adjectiveNodes) > 0:
            for node in adjectiveNodes:
                # Add new term into adjective node in order to grow our vocabulary
                if propAdjective not in self.DRSGraph.graph.node[node][CONST_NODE_VALUE_KEY]:
                    # TODO: SEE IF I CAN CHANGE THIS  TO NOT USE THIS FUNCTION
                    self.DRSGraph.AppendValueAtSpecificNode(node, propAdjective)
                propertyNode = self.getPropertyNodeFromAdjective(node)
                self.nodesWithGivenProperty.append(propertyNode)
                # MAP FOUND PROPERTY NODE'S REF ID TO THE INCOMING REF ID
                if self.DRSGraph.graph.has_node(propertyNode):
                    DRSNodeRefID = self.DRSGraph.graph.node[propertyNode][CONST_NODE_VALUE_KEY]
                    self.newToOldRefIDMapping.update({propRefId: DRSNodeRefID})
                    self.propertyCount = self.propertyCount + 1
                    openGap = False

        if CONTROL_IDENTIFY_NEGATION == True:
            if len(antonymNodes) > 0:
                print("Negation gap identified - a node has been found that contains an antonym of one of the "
                      "provided adjectives")
                # propertyNodesWithAdjective = []
                if CONTROL_RESOLVE_NEGATION == True:
                    for node in antonymNodes:
                        # print("AntonymNode", node)
                        propertyNode = self.getPropertyNodeFromAdjective(node)
                        self.nodesWithGivenPropertyAntonym.append(propertyNode)
                        print("Negation gap resolved - an antonym has been found in the knowledge graph")
                        # MAP FOUND ANTONYM NODE'S REF ID TO THE INCOMING REF ID
                        if self.DRSGraph.graph.has_node(propertyNode):
                            DRSNodeRefID = self.DRSGraph.graph.node[propertyNode][CONST_NODE_VALUE_KEY]
                            self.newToOldRefIDMapping.update({propRefId: DRSNodeRefID})
                            self.propertyCount = self.propertyCount + 1
                            self.negationActive = True
                            openGap = False

        # If not adjective or antonym node found, make sure the reference ID gets removed
        if (len(adjectiveNodes) == 0 and len(antonymNodes) == 0) or openGap == True:
            self.newToOldRefIDMapping.update({propRefId: None})
            self.propertyCount = self.propertyCount + 1

        # ***********************************************************************************************************************************
        # If no adjective nodes are found, then we look for antonyms
        # Because of this, we are positive-biased, as if we find adjective nodes, we don't look for antonyms
        # May be a better approach to look for both and, if both are found, declare a conflict rather than assume
        # one way or the other?
        # Slower processing time though
        # ***********************************************************************************************************************************
        # else:
        # antonymNodes = self.ListOfNodesWithValueFromList(antonymList)
        # We don't want to grow the vocabulary here directly, so we skip the adding new terms
        # if (len(antonymNodes) > 0):
        #    propertyNodesWithAdjective = []
        #    for node in antonymNodes:
        #        print("AntonymNode", node)
        #        if(propAdjective not in self.DRSGraph.graph.node[node]['value']):
        #            self.DRSGraph.AppendValueAtSpecificNode(node, propAdjective)
        #        propertyNode = self.getPropertyNodeFromAdjective(node)
        #        #print("propertyNode", propertyNode)
        #        self.nodesWithGivenPropertyAntonym.append(propertyNode)

    # For predicate() predicates
    # HOW TO HANDLE SENTENCE SUB-ORDINATION?
    def question_predicate(self, predicateContents):
        # Intransitive verbs: (predName, verb, subjectRef)
        # - The SubjectRef Verbed (the man laughed, the target appears)
        # Transitive verbs: (predName, verb, subjectRef, dirObjRef)
        # - The Subjectref Verbed the dirObjRef (the task A has a group of objects H,
        # the subject L remembers the letter I)
        # Ditransitive verbs: (predName, verb, subjRef, dirObjRef, indirObjRef)
        # - The SubjectRef verbed the DirObjRef to the indirObjRef (The professor (S) gave
        # the paper (D) to the student (I))
        # Break up the predicate
        predicateComponents = predicateContents.split(',')
        numberOfComponents = len(predicateComponents)
        # Always have first three components, so only special cases are transitive/ditransitive
        # predReferenceVariable = predicateComponents[0]
        predVerb = predicateComponents[1]
        predSubjRef = predicateComponents[2]
        # Set dir/indir object references to none so we can check them for substitution
        predDirObjRef = None
        predIndirObjRef = None
        # Different cases (differing number of components)
        if numberOfComponents == 3:
            # intransitive
            predSubjRef = predSubjRef.split(')')[0]
        elif numberOfComponents == 4:
            # Transitive
            predDirObjRef = predicateComponents[3].split(')')[0]
        elif numberOfComponents == 5:
            # Ditransitive
            predIndirObjRef = predicateComponents[4].split(')')[0]
        else:
            # invalid
            raise ValueError('Too many components ?')
        # Hardcode be case for specific scenarios

        # Substitute in DRS equivalents for dereferenced ref IDs
        if predSubjRef in self.newToOldRefIDMapping:
            predSubjRef = self.newToOldRefIDMapping.get(predSubjRef)
            # if predSubjRef is None:
            #    # TODO: Better define this error case
            #    if CONTROL_IDENTIFY_LEXICAL:
            #        print("Lexical gap encountered - a term was encountered which is not currently in the system's "
            #              "vocabulary.")
            #    return None
        if predDirObjRef is not None and predDirObjRef in self.newToOldRefIDMapping:
            predDirObjRef = self.newToOldRefIDMapping.get(predDirObjRef)
            # if predDirObjRef is None:
            #    # TODO: Better define this error case
            #    if CONTROL_IDENTIFY_LEXICAL:
            #        print("Lexical gap encountered - a term was encountered which is not currently in the system's "
            #              "vocabulary.")
            #        return None
        if predIndirObjRef is not None and predIndirObjRef in self.newToOldRefIDMapping:
            predIndirObjRef = self.newToOldRefIDMapping.get(predIndirObjRef)
            # if predIndirObjRef is None:
            #    # TODO: Better define this error case
            #    if CONTROL_IDENTIFY_LEXICAL:
            #        print("Lexical gap encountered - a term was encountered which is not currently in the system's "
            #              "vocabulary.")
            #        return None
        self.handleActionQuestion(numberOfComponents, predVerb, predSubjRef, predDirObjRef)

    def handleActionQuestion(self, numberOfComponents, predVerb, predSubjRef, predDirObjRef=None):
        if numberOfComponents == 3:
            pass
        elif numberOfComponents == 4:
            # Get action node by its name
            actionNode = self.findActionNodeWithVerb(predVerb)
            if CONTROL_IDENTIFY_LEXICAL is True:
                if actionNode is None and self.verbTargetGap == False:
                    print("Lexical gap encountered - a verb (" + predVerb + ") was introduced which is not currently "
                                                                            "in the system's vocabulary.")
                    if CONTROL_RESOLVE_LEXICAL is True:
                        newNymCount = 0
                        # TODO: Allow user to manually choose yes/no to resolve?
                        while actionNode is None and newNymCount < 3:
                            # No nodes "active"
                            newVerb = requestNewTermToNymCheck(predVerb)
                            newNymCount = newNymCount + 1
                            actionNode = self.findActionNodeWithVerb(newVerb)
                            if actionNode is not None:
                                print("Lexical gap resolved - a role given (" + newVerb + ") was found associated with "
                                                                                      "an item in the knowledge base")
                                self.DRSGraph.AppendValueAtSpecificNode(actionNode, newVerb)
            # actionNode = self.findActionNodeConnectedToVerbNode(verbNode)
            # If the SUBJECT reference is a proper name
            # Check if we find a node containing said name
            if predSubjRef is not None:
                if CONST_PRED_SUBJ_NAMED in predSubjRef:
                    # Get item name out of "named(XYZ)"
                    itemName = predSubjRef[predSubjRef.find("(") + 1:predSubjRef.find(")")]
                    # Add quotes around item name to actually find them since they are added on naming
                    itemName = "\"" + itemName + "\""
                    nodesWithGivenName = self.ListOfNodesWithValue(itemName)
                    if len(nodesWithGivenName) > 0:
                        itemNodes = []
                        for nameNode in nodesWithGivenName:
                            # Need to get the actual item node, not the name node.
                            itemNode = self.findItemNodeConnectedToNameNode(nameNode)
                            itemNodes.append(itemNode)
                        # If only one item with that name, then we've found our subject node
                        if len(itemNodes) == 1:
                            self.subjectNode = itemNodes[0]
            # Same as above for OBJECT reference
            if predDirObjRef is not None:
                if CONST_PRED_SUBJ_NAMED in predDirObjRef:
                    # Get item name out of "named(XYZ)"
                    # Goes all the way to the end because the closed paren has already been stripped if it's the last
                    # item
                    itemName = predDirObjRef[predDirObjRef.find("(") + 1:]
                    # Add quotes around item name to actually find them since they are added on naming
                    itemName = "\"" + itemName + "\""
                    nodesWithGivenName = self.ListOfNodesWithValue(itemName)
                    if len(nodesWithGivenName) > 0:
                        itemNodes = []
                        for nameNode in nodesWithGivenName:
                            # Need to get the actual item node, not the name node.
                            itemNode = self.findItemNodeConnectedToNameNode(nameNode)
                            itemNodes.append(itemNode)
                        # If only one item with that name, then we've found our subject node
                        if len(itemNodes) == 1:
                            self.objectNode = itemNodes[0]
            # Get the subject node
            if self.subjectNode is None:
                subjectNode = self.DRSGraph.FindItemWithValue(predSubjRef)
            else:
                subjectNode = self.subjectNode
            # Get the object nodes
            if self.objectNode is None:
                objectNode = self.DRSGraph.FindItemWithValue(predDirObjRef)
            else:
                objectNode = self.objectNode
            # If both are connected to the action node, then the action links them
            subjectNodeConnected = False
            objectNodeConnected = False
            # Check if the subject node has an "IsTargetOf" or "IsSourceOf" relationship with the action node
            if self.HasEdgeWithValue(actionNode, subjectNode, CONST_HAS_TARGET_EDGE) or \
                    self.HasEdgeWithValue(actionNode, subjectNode, CONST_HAS_SOURCE_EDGE):
                subjectNodeConnected = True
            # Check if the object node has an "IsTargetOf" or "IsSourceOf" relationship with the action node
            if self.HasEdgeWithValue(actionNode, objectNode, CONST_HAS_TARGET_EDGE) or \
                    self.HasEdgeWithValue(actionNode, objectNode, CONST_HAS_SOURCE_EDGE):
                objectNodeConnected = True
            if subjectNodeConnected is True and objectNodeConnected is True:
                self.subjectNode = subjectNode
                self.objectNode = objectNode
                self.predicateTrue = True
            # Else, unknown/no?

    def resolveQuestion(self):
        # Possibly not an actual error condition, just testing this
        # if self.objectNode is None or self.subjectNode is None:
        #    print("Either the subject or object is missing, so something is wrong")
        #    return None
        if self.predicateTrue == True:
            if self.negationActive == True:
                return False
            else:
                return True
        else:
            # Assuming that if there is one item and one property, the item is the subject node,
            if self.itemCount == 1 and self.propertyCount == 1:
                # Try to find positive relationships
                for node in self.nodesWithGivenProperty:
                    # Get the edges between the subject and object nodes
                    edgeBetweenNodes = self.DRSGraph.graph.get_edge_data(self.subjectNode, self.objectNode)
                    # Iterate through each edge connecting the two nodes if not empty list
                    if edgeBetweenNodes is not None:
                        for edge in edgeBetweenNodes.values():
                            # Get the name of the edge
                            edgeValue = edge[CONST_NODE_VALUE_KEY]
                            # If the edge is "Is" then the item has this property and we consider it TRUE
                            if edgeValue == CONST_IS_EDGE:
                                return True
                # Try to find negative relationships (antonyms)
                for antonymNode in self.nodesWithGivenPropertyAntonym:
                    # Get the edges between the subject and object nodes
                    edgeBetweenNodes = self.DRSGraph.graph.get_edge_data(self.subjectNode, self.objectNode)
                    # Iterate through each edge connecting the two nodes if not empty list
                    if edgeBetweenNodes is not None:
                        for edge in edgeBetweenNodes.values():
                            # Get the name of the edge
                            edgeValue = edge[CONST_NODE_VALUE_KEY]
                            # If the edge is "Is" then the item has this property and we consider it TRUE
                            if edgeValue == CONST_IS_EDGE:
                                return False
                # If could not find a positive or negative relationship, then return None (unknown)
                return None
            # Assuming if there are two items, there are no properties in the predicate (again, may need corrections)
            # TODO: This should learn to deal with predicates
            if self.itemCount == 2:
                edgeBetweenNodes = self.DRSGraph.graph.get_edge_data(self.subjectNode, self.objectNode)
                # Iterate through each edge connecting the two nodes if not empty list
                if edgeBetweenNodes is not None:
                    for edge in edgeBetweenNodes.values():
                        # Get the name of the edge
                        edgeValue = edge[CONST_NODE_VALUE_KEY]
                        # If IsEquivalentTo edge is found connecting the subject node and the object node then TRUE
                        if edgeValue == CONST_IS_EQUIVALENT_EDGE:
                            return True
                    # If IsEquivalentTo edge is not found connecting the subject node and the object node then FALSE
                    return False
                # TODO: This is probably not right
                if self.predicateTrue is True:
                    return True
            # If we reach this, probably a question about "Is there a ..." which as been found true
            if self.itemCount == 1:
                return True
                # If none of the above scenarios has occurred, then unknown
        return None

    # TODO: OPTIMIZE, THIS IS HIGHLY INEFFICIENT
    def HasEdgeWithValue(self, node1, node2, value):
        # Iterate through edges connected to either of the input nodes and look if they are connected
        # By an edge with the requested value
        for (n1, n2, datum) in self.DRSGraph.graph.edges([node1, node2], data=True):
            # Check both variations of this just in case
            if n1 == node1 and n2 == node2 and datum[CONST_NODE_VALUE_KEY] == value:
                return True
            if n1 == node2 and n2 == node1 and datum[CONST_NODE_VALUE_KEY] == value:
                return True
        return False

    def ListOfNodesWithValueFromList(self, listOfNyms):
        nodeList = []
        for valueToFind in listOfNyms:
            if self.DRSGraph is not None:
                # iterate through all graph nodes
                for node, values in self.DRSGraph.graph.nodes.data():
                    listOfValuesToCheck = values[CONST_NODE_VALUE_KEY].split('|')
                    for value in listOfValuesToCheck:
                        if valueToFind == value:
                            nodeList.append(node)
        return nodeList

    def ListOfNodesWithValue(self, valueToFind):
        nodeList = []
        if self.DRSGraph is not None:
            # iterate through all graph nodes
            for node, values in self.DRSGraph.graph.nodes.data():
                # If the current Node's value = the value passed in
                # Changed from valueToFind in values to valueToFind == values as "active" was
                # triggering found in "inactive" due to being substr
                listOfValuesToCheck = values[CONST_NODE_VALUE_KEY].split('|')
                for value in listOfValuesToCheck:
                    if valueToFind == value:
                        nodeList.append(node)
        return nodeList

    def getPropertyNodeFromAdjective(self, adjectiveNode):
        # Get list of edges from the node
        inEdgesFromNode = self.DRSGraph.graph.in_edges(adjectiveNode, data=True)
        outEdgesFromNode = self.DRSGraph.graph.out_edges(adjectiveNode, data=True)
        edgesFromNode = list(inEdgesFromNode) + list(outEdgesFromNode)
        for startNode, endNode, edgeValues in edgesFromNode:
            # If an edge has the value ItemHasName, then we want to modify the end node
            if edgeValues[CONST_NODE_VALUE_KEY] == CONST_PROP_HAS_ADJECTIVE_EDGE:
                # Update graph with name
                return startNode

    def findMatchingItemNode(self, role, operator, count):
        itemNodes = []
        matchingNodes = []
        # Get list of nodes with the given role
        roleNodes = self.ListOfNodesWithValue(role)
        # Handle role nodes
        # Get list of item nodes associated with the role nodes
        for roleNode in roleNodes:
            itemNodes.append(self.findItemNodeConnectedToRoleNode(roleNode))
        # Handle remaining matching nodes - check their operator and count nodes
        for itemNode in itemNodes:
            opNode = self.findOpNodeConnectedToItemNode(itemNode)
            countNode = self.findCountNodeConnectedToItemNode(itemNode)
            if self.DRSGraph.graph.nodes[opNode][CONST_NODE_VALUE_KEY] == operator and \
                    self.DRSGraph.graph.nodes[countNode][CONST_NODE_VALUE_KEY] == count:
                matchingNodes.append(itemNode)
        if CONTROL_IDENTIFY_TARGET is True:
            if len(matchingNodes) > 1:
                # RAISE A GAP HERE, Found more than one possible node with this value. Have user select.
                print("TARGET GAP: More than one node found that describes an item with the role of " + role +
                      ", the operator of " + operator + ", and the count of " + count + ".")
                if CONTROL_RESOLVE_TARGET is True:
                    print("DEBUG OPTION: Please select which node you would like to use.")
                    print(matchingNodes)
                    nodeSelected = input("Enter a node value")
                    while nodeSelected not in matchingNodes:
                        nodeSelected = input("Enter a node value")
                    return nodeSelected
        if len(matchingNodes) > 0:
            return matchingNodes.pop()
        else:
            return None

    # TODO: NEED TO HANDLE CASE WHERE MULTIPLE ITEMS
    # TEMP UNTIL FIGURE OUT NAME HANDLING
    def findItemNodeWithRole(self, strRole):
        # Get list of nodes with the given role
        roleNodes = self.ListOfNodesWithValue(strRole)
        # Handle role nodes
        # Get list of item nodes associated with the role nodes
        for roleNode in roleNodes:
            roleItemNode = self.findItemNodeConnectedToRoleNode(roleNode)
            return roleItemNode

    # TODO: NEED TO HANDLE CASE WHERE MULTIPLE POSSIBLE ACTIONS
    def findActionNodeWithVerb(self, verb):
        # Declare list of found nodes
        actionNodes = []
        # Get list of nodes with the given role
        verbNodes = self.ListOfNodesWithValue(verb)
        # Handle role nodes
        # Get list of item nodes associated with the role nodes
        for verbNode in verbNodes:
            verbActionNode = self.findActionNodeConnectedToVerbNode(verbNode)
            if verbActionNode is not None:
                # If an action node is found which has this verb, add it to the list.
                actionNodes.append(verbActionNode)
        # If there are multiple action nodes with the same verb, identify a target gap and ask the user to pick
        # which verb should be used.
        # THIS COULD HAVE AUTOMATED RESOLUTION BY LOOKING AT CONNECTED OBJECT NODES
        if CONTROL_IDENTIFY_TARGET is True:
            if len(actionNodes) > 1:
                # RAISE A GAP HERE, Found more than one possible node with this value. Have user select.
                print("TARGET GAP: More than one action node found that describes an action with the verb " + verb
                      + ".")
                self.verbTargetGap = True
                if CONTROL_RESOLVE_TARGET is True:
                    print("DEBUG OPTION: Please select which action node you would like to use.")
                    print(actionNodes)
                    nodeSelected = input("Enter a node value")
                    while nodeSelected not in actionNodes:
                        nodeSelected = input("Enter a node value")
                    return nodeSelected
            # elif len(actionNodes) == 0:
            # NO NODE FOUND matching the description given
            # print("TARGET GAP: No node found that describes an action with the verb " + verb + ".")
        # If only one action node, then we know we've found the right action
        if len(actionNodes) == 1:
            return actionNodes.pop()
        # If no action nodes found or if multiple found, we can't be certain of which action is correct.
        else:
            return None

    def findItemNodeWithNameAndRole(self, strName, strRole):
        # Get list of nodes with the given name
        nameNodes = self.ListOfNodesWithValue(strName)
        # Get list of nodes with the given role
        roleNodes = self.ListOfNodesWithValue(strRole)
        # Handle name nodes
        nameItemNodes = []
        # Get list of item nodes associated with the name nodes
        for nameNode in nameNodes:
            nameItemNode = self.findItemNodeWithName(nameNode)
            nameItemNodes.append(nameItemNode)
        # Handle role nodes
        roleItemNodes = []
        # Get list of item nodes associated with the role nodes
        for roleNode in roleNodes:
            roleItemNode = self.findItemNodeConnectedToRoleNode(roleNode)
            roleItemNodes.append(roleItemNode)
        # Find item node which has both the name and role
        # Iterate through role nodes for arbitrary reason
        for potentialItemNode in roleItemNodes:
            if potentialItemNode in nameItemNodes:
                return potentialItemNode

    def findItemNodeConnectedToNameNode(self, nameNode):
        # Edges seem to be a little weird, so getting
        inEdgesFromNode = self.DRSGraph.graph.in_edges(nameNode, data=True)
        for startNode, endNode, edgeValues in inEdgesFromNode:
            # If an edge has the value ItemHasName, then we want to return the start node (the item node itself)
            if edgeValues[CONST_NODE_VALUE_KEY] == CONST_ITEM_HAS_NAME_EDGE:
                return startNode

    def findActionNodeConnectedToVerbNode(self, verbNode):
        # Edges seem to be a little weird, so getting
        outEdgesFromNode = self.DRSGraph.graph.out_edges(verbNode, data=True)
        inEdgesFromNode = self.DRSGraph.graph.in_edges(verbNode, data=True)
        for startNode, endNode, edgeValues in inEdgesFromNode:
            # If an edge has the value ItemHasName, then we want to return the start node (the item node itself)
            if edgeValues[CONST_NODE_VALUE_KEY] == CONST_ACTION_HAS_VERB_EDGE:
                return startNode

    def findItemNodeConnectedToRoleNode(self, roleNode):
        inEdgesFromNode = self.DRSGraph.graph.in_edges(roleNode, data=True)
        for startNode, endNode, edgeValues in inEdgesFromNode:
            # If an edge has the value ItemHasRole, then we want to return the start node (the item node itself)
            if edgeValues[CONST_NODE_VALUE_KEY] == CONST_ITEM_HAS_ROLE_EDGE:
                return startNode

    def findOpNodeConnectedToItemNode(self, itemNode):
        outEdgesFromNode = self.DRSGraph.graph.out_edges(itemNode, data=True)
        for startNode, endNode, edgeValues in outEdgesFromNode:
            # If an edge has the value ItemHasOp, then we want to return the start node (the item node itself)
            if edgeValues[CONST_NODE_VALUE_KEY] == CONST_ITEM_HAS_OP_EDGE:
                return endNode

    def findRoleNodeConnectedToItemNode(self, itemNode):
        outEdgesFromNode = self.DRSGraph.graph.out_edges(itemNode, data=True)
        for startNode, endNode, edgeValues in outEdgesFromNode:
            # If an edge has the value ItemHasRole, then we want to return the start node (the item node itself)
            if edgeValues[CONST_NODE_VALUE_KEY] == CONST_ITEM_HAS_ROLE_EDGE:
                return endNode

    def findCountNodeConnectedToItemNode(self, itemNode):
        outEdgesFromNode = self.DRSGraph.graph.out_edges(itemNode, data=True)
        for startNode, endNode, edgeValues in outEdgesFromNode:
            # If an edge has the value ItemHasCount, then we want to return the start node (the item node itself)
            if edgeValues[CONST_NODE_VALUE_KEY] == CONST_ITEM_HAS_COUNT_EDGE:
                return endNode


def requestNewTermToNymCheck(originalTerm):
    newTerm = input(
        "Sorry, I don't understand \"" + originalTerm + "\".  Please give me an alternate word and "
                                                        "I'll make the connection.")
    return newTerm


def APEWebserviceCall(phraseToDRS):
    print(phraseToDRS)
    # Make APE Webservice call with given ACE phrase
    urlToRequest = "http://attempto.ifi.uzh.ch/ws/ape/apews.perl?text=" + phraseToDRS + "&solo=drspp"
    # Get the DRS that is sent back
    r = requests.get(urlToRequest)
    returnedDRS = r.text.splitlines()
    DRSLines = []
    error = False
    for line in returnedDRS:
        line = line.strip()
        # Exclude first, useless line
        # Also skip empty lines (if line.strip() returns true if line is non-empty.)
        if line != '[]' and line.strip():
            if line == "importance=\"error\"":
                error = True
            DRSLines.append(line)
    # Technically it's a little silly to categorize the DRS for a question since it's obviously all
    # a question, but this gets around having to do questionable and inconsistent parsing to deal with
    # the header lines
    # This way, we can just get the question lines, which are what we actually use to process questions
    if error:
        return None
    else:
        symbolLines = getSymbolLines(DRSLines)
        categorizedQuestionDRS = categorizeDRSLines(DRSLines, symbolLines)

        questionLines = []
        # Iterate through DRS lines and get only the actual question lines, none of the headers
        for index, line in enumerate(DRSLines):
            if categorizedQuestionDRS.get(index) == CONST_QUESTION_TAG:
                questionLines.append(line)
        # Return just the lines that are the actual DRS for the question, no headers
        return questionLines


def getNyms(wordToCheck):
    # Iterate through all words to check
    synonyms = []
    hypernyms = []
    hyponyms = []
    deriv = []
    uniqueNymList = []
    uniqueAntonymList = []
    # Get synsets of current word to check
    testWord = wordnet.synsets(wordToCheck)
    # for each synset (meaning)
    for syn in testWord:
        # Get Hypernyms
        if len(syn.hypernyms()) > 0:
            currentHypernyms = syn.hypernyms()
            for hyperSyn in currentHypernyms:
                for lemma in hyperSyn.lemmas():
                    hypernyms.append(lemma.name())
        # Get Hyponyms
        if len(syn.hyponyms()) > 0:
            currentHyponyms = syn.hyponyms()
            for hypoSyn in currentHyponyms:
                for lemma in hypoSyn.lemmas():
                    hyponyms.append(lemma.name())
        # Get direct synonyms
        for lemma in syn.lemmas():
            synonyms.append(lemma.name())
            # Get derivationally related forms
            for derivForm in lemma.derivationally_related_forms():
                if derivForm.name() not in deriv:
                    deriv.append(derivForm.name())
            # Get antonyms
            if lemma.antonyms():
                if lemma.antonyms()[0].name() not in uniqueAntonymList:
                    uniqueAntonymList.append(lemma.antonyms()[0].name())
        nymLists = synonyms + hypernyms + hyponyms + deriv
        uniqueNyms = set(nymLists)
        uniqueNymList = list(uniqueNyms)
    return uniqueNymList, uniqueAntonymList


# HORRIBLY INEFFICIENT, BUT PROOF OF CONCEPT SO IT'S OKAY
def checkForContextGap(DRSGraph):
    # Get all the nodes in the graph
    graphNodes = DRSGraph.graph.nodes()
    # Establish the regex patterns to find the nodes of interest (in this case ItemX and PropertyX)
    itemNodePattern = re.compile(CONST_REGEX_ITEM_NODE)
    propertyNodePattern = re.compile(CONST_REGEX_PROPERTY_NODE)
    # Identify the usual attribute edges which we want to ignore
    itemEdgesToIgnore = [CONST_ITEM_HAS_NAME_EDGE, CONST_ITEM_HAS_AFFORDANCE_EDGE, CONST_ITEM_HAS_DESCRIPTION_EDGE,
                         CONST_ITEM_HAS_ROLE_EDGE, CONST_ITEM_HAS_OP_EDGE, CONST_ITEM_HAS_COUNT_EDGE]
    propertyEdgesToIgnore = [CONST_PROP_HAS_ADJECTIVE_EDGE, CONST_PROP_HAS_SEC_OBJECT_EDGE,
                             CONST_PROP_HAS_TERT_OBJECT_EDGE, CONST_PROP_HAS_DEG_EDGE, CONST_PROP_HAS_COMP_TARGET_EDGE]
    # Isolate the item and property nodes
    itemNodes = []
    propertyNodes = []
    for node in graphNodes:
        if re.match(itemNodePattern, node):
            itemNodes.append(node)
        elif re.match(propertyNodePattern, node):
            propertyNodes.append(node)

    # Iterate through all the main ItemX nodes
    for itemNode in itemNodes:
        # Set the number of contextual edges for this node to none
        contextualEdges = 0
        # Get all the edges for the node
        inEdgesFromNode = DRSGraph.graph.in_edges(itemNode, data=True)
        outEdgesFromNode = DRSGraph.graph.out_edges(itemNode, data=True)
        edgesFromNode = list(inEdgesFromNode) + list(outEdgesFromNode)
        # For each edge in the node
        for startNode, endNode, edgeData in edgesFromNode:
            # Get the value of the edge
            edgeValue = edgeData[CONST_NODE_VALUE_KEY]
            # if there is an edge which we don't ignore (a contextual edge), then we increase that count
            if edgeValue not in itemEdgesToIgnore:
                contextualEdges = contextualEdges + 1
        # If there are no contextual edges, immediately raise a context gap
        if contextualEdges == 0:
            print("CONTEXT GAP IDENTIFIED: ", itemNode, " has no contextual edges and thus has no context in the task")

    # Iterate through all the main PropertyX nodes
    for propertyNode in propertyNodes:
        # Set the number of contextual edges for this node to none
        contextualEdges = 0
        # Get all the edges for the node
        inEdgesFromNode = DRSGraph.graph.in_edges(propertyNode, data=True)
        outEdgesFromNode = DRSGraph.graph.out_edges(propertyNode, data=True)
        edgesFromNode = list(inEdgesFromNode) + list(outEdgesFromNode)
        # For each edge in the node
        for startNode, endNode, edgeData in edgesFromNode:
            # Get the value of the edge
            edgeValue = edgeData[CONST_NODE_VALUE_KEY]
            # if there is an edge which we don't ignore (a contextual edge), then we increase that count
            if edgeValue not in propertyEdgesToIgnore:
                contextualEdges = contextualEdges + 1
        # If there are no contextual edges, immediately raise a context gap
        if contextualEdges == 0:
            print("CONTEXT GAP IDENTIFIED: ", propertyNode, " has no contextual edges and "
                                                            "thus has no context in the task")
    # Ignore the edges which are the usual ones (list of ignored edges stored in array)
    # For each main ItemX and PropertyX node, see if there are edges besides the usual attribute edges
    # If yes, no problem with that node, move on

    # If no, context gap found.


# TODO: handle 5-item predicate() tags
def DRSToItem():
    # Declare relevant variables
    DRSGraph = None
    DRSLines = []
    outputFiles = 0
    conditionalCount = 0
    # Read in DRS instructions from file
    DRSFile = open(CONST_INPUT_FILE_NAME + ".txt", "r")
    for line in DRSFile:
        # Get DRS command and remove any leading and ending whitespace
        DRSLines.append(line.strip())
    # Get numbers of which lines are headers ([A, B, C, ...] and conditionals (=>) )
    symbolLines = getSymbolLines(DRSLines)

    categorizedDRSLines = categorizeDRSLines(DRSLines, symbolLines)

    # Get all if-then sets
    conditionalSets = getConditionals(DRSLines, categorizedDRSLines)

    # print(conditionalSets)
    # Set up the predicate switcher
    predSwitcher = predicateSwitcher()

    # Set up counter for question response
    questionCounter = 1

    # Iterate through the DRS instructions
    for index, currentInstruction in enumerate(DRSLines):
        # take next instruction or exit
        nextStep = ''

        # As long as no "exit" given
        if nextStep != 'exit':
            # If the current line is an instruction
            if categorizedDRSLines.get(index) == CONST_INSTRUCTION_TAG:
                # Get the predicate type and contents
                instructionCountInMatchingIfBlock, conditionalWithMatchingIfBlock = \
                    checkCurrentInstructionIf(DRSLines, index, currentInstruction, conditionalSets)
                DRSGraph = splitAndRun(currentInstruction, predSwitcher, False)
                # If we want to export a graph for each step of the way, we do that here
                if CONTROL_EXPORT_EACH_STEP_GRAPH is True:
                    networkx.write_graphml_lxml(DRSGraph.graph, CONST_INPUT_FILE_NAME
                                                + "aINSTRUCTION_STEP" + str(outputFiles) + ".graphml")
                    # Increase the counter
                    outputFiles = outputFiles + 1
                    if currentAnnotationLine == 1 or currentAnnotationLine == 3 or currentAnnotationLine == 9 or \
                            currentAnnotationLine == 11 or currentAnnotationLine == 12 or currentAnnotationLine == 13:
                        currentACELine = currentACELine + 1
                    currentAnnotationLine = currentAnnotationLine + 1


        # Break out of loop with exit
        else:
            break

    # Reset the output counter so the conditionals are tracked separately from the instructions
    outputFiles = 0
    # On end of reading in instructions
    # process conditionals first:
    for conditional in conditionalSets:
        if not conditional.processed:
            DRSGraph = runFullConditional(conditional, predSwitcher, DRSGraph, conditionalSets, conditionalCount)
            conditionalCount = conditionalCount + 1
            # If we want to export a graph for each step of the way, we do that here
            if CONTROL_EXPORT_EACH_STEP_GRAPH is True:
                networkx.write_graphml_lxml(DRSGraph.graph, CONST_INPUT_FILE_NAME
                                            + "bCONDITIONAL_STEP" + str(outputFiles) + ".graphml")
                # Increase the counter
                outputFiles = outputFiles + 1
                currentAnnotationLine = currentAnnotationLine + 1
                if currentAnnotationLine == 1 or currentAnnotationLine == 3 or currentAnnotationLine == 9 or \
                        currentAnnotationLine == 11 or currentAnnotationLine == 12 or currentAnnotationLine == 13:
                    currentACELine = currentACELine + 1

    # Post-instruction pre-query gap identification goes here
    # In this case, Context Gap
    if CONTROL_IDENTIFY_CONTEXT is True:
        checkForContextGap(DRSGraph)

    # Set up questionSwitcher
    qSwitcher = questionSwitcher()
    questionInput = input('Please enter a question')
    # "exit" is trigger word to end questioning
    while questionInput != 'exit':
        questionLines = APEWebserviceCall(questionInput)
        while questionLines is None:
            questionInput = input('There was an error with the ACE entered - please try again.')
            questionLines = APEWebserviceCall(questionInput)

        for currentLine in questionLines:
            predicateSplit = currentLine.split('(', 1)
            predicateType = predicateSplit[0]
            predicateContents = predicateSplit[1]
            qSwitcher.callFunction(predicateType, predicateContents, DRSGraph)

        result = qSwitcher.resolveQuestion()
        if result:
            print("Question", str(questionCounter), "Answer: Yes")
        elif not result and result is not None:
            print("Question", str(questionCounter), "Answer: No")
        else:
            print("Question", str(questionCounter), "Answer: Unknown")
        questionCounter = questionCounter + 1
        # I have my doubts about these lines below but they seem to work
        DRSGraph = qSwitcher.returnDRSGraph()
        predSwitcher.updateDRSGraph(DRSGraph.graph)
        # Reset qSwitcher to be a new question switcher
        qSwitcher = questionSwitcher()
        questionInput = input('Please enter a DRS line for your question')

    # Once "exit" has been entered
    # At end of program, if an ontology was built at all, print it out and export it in GraphML
    if DRSGraph is not None:
        jsonFile = open("jsonFile.txt", "w")
        jsonSerializable = networkx.readwrite.json_graph.node_link_data(DRSGraph.graph)
        jsonOutput = json.dumps(jsonSerializable)
        jsonFile.write(jsonOutput)
        networkx.write_graphml_lxml(DRSGraph.graph, CONST_INPUT_FILE_NAME + ".graphml")


DRSToItem()
