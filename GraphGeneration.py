import networkx
from Constants import *
import re


# Create Graph
def generateItemGraph(graphNumber):
    itemGraph = networkx.MultiDiGraph()
    itemGraph.add_node(CONST_ITEM_NODE + str(graphNumber), value='')
    itemGraph.add_node(CONST_ITEM_NAME_NODE + str(graphNumber), value='')
    itemGraph.add_node(CONST_ITEM_AFFORDANCE_NODE + str(graphNumber), value='')
    itemGraph.add_node(CONST_ITEM_DESCRIPTION_NODE + str(graphNumber), value='')
    itemGraph.add_node(CONST_ITEM_ROLE_NODE + str(graphNumber), value='')
    itemGraph.add_node(CONST_ITEM_OP_NODE + str(graphNumber), value='')
    itemGraph.add_node(CONST_ITEM_COUNT_NODE + str(graphNumber), value='')

    itemGraph.add_edge(CONST_ITEM_NODE + str(graphNumber), CONST_ITEM_NAME_NODE + str(graphNumber),
                       value=CONST_ITEM_HAS_NAME_EDGE)
    itemGraph.add_edge(CONST_ITEM_NODE + str(graphNumber), CONST_ITEM_AFFORDANCE_NODE + str(graphNumber),
                       value=CONST_ITEM_HAS_AFFORDANCE_EDGE)
    itemGraph.add_edge(CONST_ITEM_NODE + str(graphNumber), CONST_ITEM_DESCRIPTION_NODE + str(graphNumber),
                       value=CONST_ITEM_HAS_DESCRIPTION_EDGE)
    itemGraph.add_edge(CONST_ITEM_NODE + str(graphNumber), CONST_ITEM_ROLE_NODE + str(graphNumber),
                       value=CONST_ITEM_HAS_ROLE_EDGE)
    itemGraph.add_edge(CONST_ITEM_NODE + str(graphNumber), CONST_ITEM_OP_NODE + str(graphNumber),
                       value=CONST_ITEM_HAS_OP_EDGE)
    itemGraph.add_edge(CONST_ITEM_NODE + str(graphNumber), CONST_ITEM_COUNT_NODE + str(graphNumber),
                       value=CONST_ITEM_HAS_COUNT_EDGE)

    return itemGraph


def generatePropGraph(graphNumber):
    propGraph = networkx.MultiDiGraph()
    propGraph.add_node(CONST_PROP_NODE + str(graphNumber), value='')
    propGraph.add_node(CONST_PROP_ADJECTIVE_NODE + str(graphNumber), value='')
    propGraph.add_node(CONST_PROP_SEC_OBJECT_NODE + str(graphNumber), value='')
    propGraph.add_node(CONST_PROP_TERT_OBJECT_NODE + str(graphNumber), value='')
    propGraph.add_node(CONST_PROP_DEG_NODE + str(graphNumber), value='')
    propGraph.add_node(CONST_PROP_COMP_TARGET_NODE + str(graphNumber), value='')

    propGraph.add_edge(CONST_PROP_NODE + str(graphNumber), CONST_PROP_ADJECTIVE_NODE + str(graphNumber),
                       value=CONST_PROP_HAS_ADJECTIVE_EDGE)
    propGraph.add_edge(CONST_PROP_NODE + str(graphNumber), CONST_PROP_SEC_OBJECT_NODE + str(graphNumber),
                       value=CONST_PROP_HAS_SEC_OBJECT_EDGE)
    propGraph.add_edge(CONST_PROP_NODE + str(graphNumber), CONST_PROP_TERT_OBJECT_NODE + str(graphNumber),
                       value=CONST_PROP_HAS_TERT_OBJECT_EDGE)
    propGraph.add_edge(CONST_PROP_NODE + str(graphNumber), CONST_PROP_DEG_NODE + str(graphNumber),
                       value=CONST_PROP_HAS_DEG_EDGE)
    propGraph.add_edge(CONST_PROP_NODE + str(graphNumber), CONST_PROP_COMP_TARGET_NODE + str(graphNumber),
                       value=CONST_PROP_HAS_COMP_TARGET_EDGE)

    return propGraph


def generateActionGraph(graphNumber):
    actionGraph = networkx.MultiDiGraph()
    actionGraph.add_node(CONST_ACTION_NODE + str(graphNumber), value='')
    actionGraph.add_node(CONST_ACTION_VERB_NODE + str(graphNumber), value='')

    actionGraph.add_edge(CONST_ACTION_NODE + str(graphNumber), CONST_ACTION_VERB_NODE + str(graphNumber),
                         value=CONST_ACTION_HAS_VERB_EDGE)

    return actionGraph


def generateModPPGraph(graphNumber):
    modPPGraph = networkx.MultiDiGraph()
    modPPGraph.add_node(CONST_MODPP_NODE + str(graphNumber), value='')
    modPPGraph.add_node(CONST_MODPP_PREP_NODE + str(graphNumber), value='')

    modPPGraph.add_edge(CONST_MODPP_NODE + str(graphNumber), CONST_MODPP_PREP_NODE + str(graphNumber),
                        value=CONST_MODPP_HAS_PREP_EDGE)

    return modPPGraph


def generateRelationGraph(graphNumber):
    relationGraph = networkx.MultiDiGraph()
    relationGraph.add_node(CONST_RELATION_NODE + str(graphNumber), value=CONST_RELATION_NODE + str(graphNumber))

    return relationGraph


def generateConditionalGraph(graphNumber):
    conditionalGraph = networkx.MultiDiGraph()
    conditionalGraph.add_node(CONST_CONDITIONAL_NODE + str(graphNumber), value=CONST_CONDITIONAL_NODE + str(graphNumber))

    return conditionalGraph


class ItemGraph(object):
    # Constructor
    def __init__(self, graphNumber):
        self.graphNumber = graphNumber
        if graphNumber is not None:
            self.graph = generateItemGraph(self.graphNumber)
        else:
            self.graph = None

    # Generic append method based on whatever target is passed in
    def __append(self, target, newValue):
        currentValue = self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY]
        if currentValue == '':
            updatedValue = newValue
        else:
            # Check if new value is already in the current value
            newValuePattern = re.compile('\\b' + newValue + '\\b')
            if re.search(newValuePattern, currentValue):
                updatedValue = currentValue
            else:
                updatedValue = currentValue + '|' + newValue
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = updatedValue

    # Generic replace method based on whatever target is passed in
    def __replace(self, target, newValue):
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = newValue

    # Append/replace methods for each node value in Item Graph
    def appendItemValue(self, newValue):
        self.__append(CONST_ITEM_NODE, newValue)

    def replaceItemValue(self, newValue):
        self.__replace(CONST_ITEM_NODE, newValue)

    def appendItemName(self, newName):
        self.__append(CONST_ITEM_NAME_NODE, newName)

    def replaceItemName(self, newName):
        self.__replace(CONST_ITEM_NAME_NODE, newName)

    def appendItemAffordance(self, newAffordance):
        self.__append(CONST_ITEM_AFFORDANCE_NODE, newAffordance)

    def replaceItemAffordance(self, newAffordance):
        self.__replace(CONST_ITEM_AFFORDANCE_NODE, newAffordance)

    def appendItemDescription(self, newDescription):
        self.__append(CONST_ITEM_DESCRIPTION_NODE, newDescription)

    def replaceItemDescription(self, newDescription):
        self.__replace(CONST_ITEM_DESCRIPTION_NODE, newDescription)

    def appendItemRole(self, newRole):
        self.__append(CONST_ITEM_ROLE_NODE, newRole)

    def replaceItemRole(self, newRole):
        self.__replace(CONST_ITEM_ROLE_NODE, newRole)

    def appendItemOp(self, newOp):
        self.__append(CONST_ITEM_OP_NODE, newOp)

    def replaceItemOp(self, newOp):
        self.__replace(CONST_ITEM_OP_NODE, newOp)

    def appendItemCount(self, newCount):
        self.__append(CONST_ITEM_COUNT_NODE, newCount)

    def replaceItemCount(self, newCount):
        self.__replace(CONST_ITEM_COUNT_NODE, newCount)

    # Method to find a node containing a given value
    def FindItemWithValue(self, valueToFind):
        if self.graph is not None:
            # iterate through all graph nodes
            for node, values in self.graph.nodes.data():
                # If the current Node's value = the value passed in
                if values[CONST_NODE_VALUE_KEY] == valueToFind:
                    return node
        return None

    # Methods to add different types of edges between nodes
    def addGroupMembershipEdges(self, groupNode, memberNode):
        self.graph.add_edge(memberNode, groupNode, value=CONST_IS_MEMBER_EDGE)
        self.graph.add_edge(groupNode, memberNode, value=CONST_HAS_MEMBER_EDGE)

    def addNodeEquivalencyEdges(self, firstNode, secondNode):
        self.graph.add_edge(firstNode, secondNode, value=CONST_IS_EQUIVALENT_EDGE)
        self.graph.add_edge(secondNode, firstNode, value=CONST_IS_EQUIVALENT_EDGE)

    def addCompositionEdges(self, composedNode, partOfNode):
        self.graph.add_edge(composedNode, partOfNode, value=CONST_HAS_A_EDGE)
        self.graph.add_edge(partOfNode, composedNode, value=CONST_IS_PART_OF_EDGE)

    def addPropertyEdge(self, objectNode, propertyNode):
        self.graph.add_edge(objectNode, propertyNode, value=CONST_IS_EDGE)

    # Methods to add different types of edges between nodes
    def addActionPerformerEdges(self, performerNode, actionNode):
        self.graph.add_edge(performerNode, actionNode, value=CONST_IS_SOURCE_EDGE)
        self.graph.add_edge(actionNode, performerNode, value=CONST_HAS_SOURCE_EDGE)

    def addActionTargetEdges(self, actionNode, targetNode):
        self.graph.add_edge(actionNode, targetNode, value=CONST_HAS_TARGET_EDGE)
        self.graph.add_edge(targetNode, actionNode, value=CONST_IS_TARGET_EDGE)

    def addModifierVerbEdges(self, modifierNode, verbNode):
        self.graph.add_edge(modifierNode, verbNode, value=CONST_MODIFIES_VERB_EDGE)
        self.graph.add_edge(verbNode, modifierNode, value=CONST_IS_MODIFIED_EDGE)

    def addModifierObjectEdges(self, modifierNode, objectNode):
        self.graph.add_edge(modifierNode, objectNode, value=CONST_MODIFIES_OBJECT_EDGE)
        self.graph.add_edge(objectNode, modifierNode, value=CONST_IS_MODIFIED_EDGE)

    def addRelationAttributeEdges(self, attributeNode, relationNode):
        self.graph.add_edge(attributeNode, relationNode, value=CONST_RELATION_IS_ATTRIBUTE_EDGE)
        self.graph.add_edge(relationNode, attributeNode, value=CONST_RELATION_HAS_PARENT_EDGE)

    def addRelationParentEdges(self, parentNode, relationNode):
        self.graph.add_edge(parentNode, relationNode, value=CONST_RELATION_IS_PARENT_EDGE)
        self.graph.add_edge(relationNode, parentNode, value=CONST_RELATION_HAS_ATTRIBUTE_EDGE)

    # Add positive conditional trigger edge between nodes - POSSIBLY DEPRECATED
    def addConditionalTriggerEdges(self, ifNodeValue, thenNodeValue):
        ifNode = self.FindItemWithValue(ifNodeValue)
        thenNode = self.FindItemWithValue(thenNodeValue)
        # We only want to trigger actions, not statement
        if ifNode is not None and thenNode is not None:
            if CONST_ACTION_NODE in thenNode:
                self.graph.add_edge(ifNode, thenNode, value=CONST_TRIGGERS_IF_TRUE_EDGE)
                self.graph.add_edge(thenNode, ifNode, value=CONST_TRIGGERED_BY_EDGE)

    # Add negative conditional trigger edge between nodes - POSSIBLY DEPRECATED
    def addConditionalNegationTriggerEdges(self, ifNodeValue, thenNodeValue):
        ifNode = self.FindItemWithValue(ifNodeValue)
        thenNode = self.FindItemWithValue(thenNodeValue)
        # We only want to trigger actions, not statement
        if ifNode is not None and thenNode is not None:
            if CONST_ACTION_NODE in thenNode:
                self.graph.add_edge(ifNode, thenNode, value=CONST_TRIGGERS_IF_FALSE_EDGE)
                self.graph.add_edge(thenNode, ifNode, value=CONST_TRIGGERED_BY_EDGE)

    # Add positive condition edge between if node and conditional node
    def addConditionalConditionEdges(self, ifNodeValue, conditionalNodeValue):
        ifNode = self.FindItemWithValue(ifNodeValue)
        conditionalNode = self.FindItemWithValue(conditionalNodeValue)
        # We only want to trigger conditionals, not statement
        if ifNode is not None and conditionalNode is not None:
            if CONST_CONDITIONAL_NODE in conditionalNode:
                self.graph.add_edge(ifNode, conditionalNode, value=CONST_TRUE_CONDITION_OF_EDGE)
                self.graph.add_edge(conditionalNode, ifNode, value=CONST_HAS_TRUE_CONDITION_EDGE)

    # Add negative condition edge between if node and conditional node
    def addConditionalNegationConditionEdges(self, ifNodeValue, conditionalNodeValue):
        ifNode = self.FindItemWithValue(ifNodeValue)
        conditionalNode = self.FindItemWithValue(conditionalNodeValue)
        # We only want to trigger conditionals, not statement
        if ifNode is not None and conditionalNode is not None:
            if CONST_CONDITIONAL_NODE in conditionalNode:
                self.graph.add_edge(ifNode, conditionalNode, value=CONST_FALSE_CONDITION_OF_EDGE)
                self.graph.add_edge(conditionalNode, ifNode, value=CONST_HAS_FALSE_CONDITION_EDGE)

    # Add consequence edge between then node and conditional node
    def addConditionalConsequenceEdges(self, thenNodeValue, conditionalNodeValue):
        thenNode = self.FindItemWithValue(thenNodeValue)
        conditionalNode = self.FindItemWithValue(conditionalNodeValue)
        # We only want to trigger conditionals, not statement
        if thenNode is not None and conditionalNode is not None:
            if CONST_CONDITIONAL_NODE in conditionalNode:
                self.graph.add_edge(thenNode, conditionalNode, value=CONST_CONSEQUENCE_OF_EDGE)
                self.graph.add_edge(conditionalNode, thenNode, value=CONST_HAS_CONSEQUENCE_EDGE)

    # Methods to replace values of specific nodes
    def ReplaceItemAffordanceAtSpecificNode(self, nodeToAddAffordance, newAffordance):
        node = self.FindItemWithValue(nodeToAddAffordance)
        if node is not None:
            edgesFromNode = self.graph.edges(node, data=True)
            for startNode, endNode, edgeValues in edgesFromNode:
                # If an edge has the value ItemHasName, then we want to modify the end node
                if edgeValues[CONST_NODE_VALUE_KEY] == CONST_ITEM_HAS_AFFORDANCE_EDGE:
                    # Update graph with name
                    self.graph.nodes(data=True)[endNode][CONST_NODE_VALUE_KEY] = newAffordance
                    return True
        else:
            print("No node with direct object reference as value found")
            return False

    # TODO: UPDATE THIS TO USE __append
    # Methods to replace values of specific nodes
    def AppendItemAffordanceAtSpecificNode(self, nodeToAddAffordance, newAffordance):
        node = self.FindItemWithValue(nodeToAddAffordance)
        if node is not None:
            edgesFromNode = self.graph.edges(node, data=True)
            for startNode, endNode, edgeValues in edgesFromNode:
                # If an edge has the value ItemHasName, then we want to modify the end node
                if edgeValues[CONST_NODE_VALUE_KEY] == CONST_ITEM_HAS_AFFORDANCE_EDGE:
                    # Update graph with name
                    currentValue = self.graph.nodes(data=True)[endNode][CONST_NODE_VALUE_KEY]
                    if currentValue == '':
                        updatedValue = newAffordance
                    else:
                        # Check if new value is already in the current value
                        newValuePattern = re.compile(r"(^|\|)" + newAffordance + r"(\||$)")
                        if re.search(newValuePattern, currentValue):
                            updatedValue = currentValue
                        else:
                            updatedValue = currentValue + '|' + newAffordance
                    self.graph.nodes(data=True)[endNode][CONST_NODE_VALUE_KEY] = updatedValue
                    return True
        else:
            print("No node with direct object reference as value found")
            return False

    # Methods to replace values of specific nodes
    def AppendValueAtSpecificNode(self, nodeToAddValue, newValue):
        # Update graph with name
        currentValue = self.graph.nodes(data=True)[nodeToAddValue][CONST_NODE_VALUE_KEY]
        if currentValue == '':
            updatedValue = newValue
        else:
            # Check if new value is already in the current value
            newValuePattern = re.compile('\\b' + newValue + '\\b')
            if re.search(newValuePattern, currentValue):
                updatedValue = currentValue
            else:
                updatedValue = currentValue + '|' + newValue
        self.graph.nodes(data=True)[nodeToAddValue][CONST_NODE_VALUE_KEY] = updatedValue
        return True

    def ReplaceItemNameAtSpecificNode(self, nodeToAddName, newName):
        # Find Node
        node = self.FindItemWithValue(nodeToAddName)
        if node is not None:
            # Get list of edges from the node
            edgesFromNode = self.graph.edges(node, data=True)
            for startNode, endNode, edgeValues in edgesFromNode:
                # If an edge has the value ItemHasName, then we want to modify the end node
                if edgeValues[CONST_NODE_VALUE_KEY] == CONST_ITEM_HAS_NAME_EDGE:
                    # Update graph with name
                    self.graph.nodes(data=True)[endNode][CONST_NODE_VALUE_KEY] = newName
                    return True
        else:
            print("No node with direct object reference as value found")
            return False


class PropertyGraph(object):
    # Constructor
    def __init__(self, graphNumber):
        self.graphNumber = graphNumber
        if graphNumber is not None:
            self.graph = generatePropGraph(self.graphNumber)
        else:
            self.graph = None

    # Generic append method based on whatever target is passed in
    def __append(self, target, newValue):
        currentValue = self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY]
        if currentValue == '':
            updatedValue = newValue
        else:
            # Check if new value is already in the current value
            newValuePattern = re.compile('\\b' + newValue + '\\b')
            if re.search(newValuePattern, currentValue):
                updatedValue = currentValue
            else:
                updatedValue = currentValue + '|' + newValue
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = updatedValue

    # Generic replace method based on whatever target is passed in
    def __replace(self, target, newValue):
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = newValue

    # Append/replace methods for each node value in Property Graph
    def appendPropValue(self, newValue):
        self.__append(CONST_PROP_NODE, newValue)

    def replacePropValue(self, newValue):
        self.__replace(CONST_PROP_NODE, newValue)

    def appendPropAdj(self, newAdjective):
        self.__append(CONST_PROP_ADJECTIVE_NODE, newAdjective)

    def replacePropAdj(self, newAdjective):
        self.__replace(CONST_PROP_ADJECTIVE_NODE, newAdjective)

    def appendPropSecObj(self, newSecondaryObject):
        self.__append(CONST_PROP_SEC_OBJECT_NODE, newSecondaryObject)

    def replacePropSecObj(self, newSecondaryObject):
        self.__replace(CONST_PROP_SEC_OBJECT_NODE, newSecondaryObject)

    def appendPropTertObj(self, newTertiaryObject):
        self.__append(CONST_PROP_TERT_OBJECT_NODE, newTertiaryObject)

    def replacePropTertObj(self, newTertiaryObject):
        self.__replace(CONST_PROP_TERT_OBJECT_NODE, newTertiaryObject)

    def appendPropDegree(self, newDegree):
        self.__append(CONST_PROP_DEG_NODE, newDegree)

    def replacePropDegree(self, newDegree):
        self.__replace(CONST_PROP_DEG_NODE, newDegree)

    def appendPropCompTarget(self, newCompTarget):
        self.__append(CONST_PROP_COMP_TARGET_NODE, newCompTarget)

    def replacePropCompTarget(self, newCompTarget):
        self.__replace(CONST_PROP_COMP_TARGET_NODE, newCompTarget)

    # Method to find a node containing a given value
    def FindPropertyWithValue(self, valueToFind):
        if self.graph is not None:
            # iterate through all graph nodes
            for node, values in self.graph.nodes.data():
                # If the current Node's value = the value passed in
                if values[CONST_NODE_VALUE_KEY] == valueToFind:
                    return node
        return None


class ActionGraph(object):
    # Constructor
    def __init__(self, graphNumber):
        self.graphNumber = graphNumber
        if graphNumber is not None:
            self.graph = generateActionGraph(self.graphNumber)
        else:
            self.graph = None

    # Generic append method based on whatever target is passed in
    def __append(self, target, newValue):
        currentValue = self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY]
        if currentValue == '':
            updatedValue = newValue
        else:
            # Check if new value is already in the current value
            newValuePattern = re.compile('\\b' + newValue + '\\b')
            if re.search(newValuePattern, currentValue):
                updatedValue = currentValue
            else:
                updatedValue = currentValue + '|' + newValue
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = updatedValue

    # Generic replace method based on whatever target is passed in
    def __replace(self, target, newValue):
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = newValue

    # Append/replace methods for each node value in Property Graph
    def appendActionValue(self, newValue):
        self.__append(CONST_ACTION_NODE, newValue)

    def replaceActionValue(self, newValue):
        self.__replace(CONST_ACTION_NODE, newValue)

    def appendActionVerb(self, newVerb):
        self.__append(CONST_ACTION_VERB_NODE, newVerb)

    def replaceActionVerb(self, newVerb):
        self.__replace(CONST_ACTION_VERB_NODE, newVerb)

    # Method to find a node containing a given value
    def FindActionWithValue(self, valueToFind):
        if self.graph is not None:
            # iterate through all graph nodes
            for node, values in self.graph.nodes.data():
                # If the current Node's value = the value passed in
                if values[CONST_NODE_VALUE_KEY] == valueToFind:
                    return node
        return None


# Modifier_PP (adv will need a different graph)
class ModifierPPGraph(object):
    # Constructor
    def __init__(self, graphNumber):
        self.graphNumber = graphNumber
        if graphNumber is not None:
            self.graph = generateModPPGraph(self.graphNumber)
        else:
            self.graph = None

    # Generic append method based on whatever target is passed in
    def __append(self, target, newValue):
        currentValue = self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY]
        if currentValue == '':
            updatedValue = newValue
        else:
            # Check if new value is already in the current value
            newValuePattern = re.compile('\\b' + newValue + '\\b')
            if re.search(newValuePattern, currentValue):
                updatedValue = currentValue
            else:
                updatedValue = currentValue + '|' + newValue
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = updatedValue

    # Generic replace method based on whatever target is passed in
    def __replace(self, target, newValue):
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = newValue

    # Append/replace methods for each node value in Property Graph
    def appendModPPValue(self, newValue):
        self.__append(CONST_MODPP_NODE, newValue)

    def replaceModPPValue(self, newValue):
        self.__replace(CONST_MODPP_NODE, newValue)

    def appendModPPPrep(self, newPreposition):
        self.__append(CONST_MODPP_PREP_NODE, newPreposition)

    def replaceModPPPrep(self, newPreposition):
        self.__replace(CONST_MODPP_PREP_NODE, newPreposition)

    # Method to find a node containing a given value
    def FindModWithValue(self, valueToFind):
        if self.graph is not None:
            # iterate through all graph nodes
            for node, values in self.graph.nodes.data():
                # If the current Node's value = the value passed in
                if values[CONST_NODE_VALUE_KEY] == valueToFind:
                    return node
        return None


# Relation Graph
class RelationGraph(object):
    # Constructor
    def __init__(self, graphNumber):
        self.graphNumber = graphNumber
        if graphNumber is not None:
            self.graph = generateRelationGraph(self.graphNumber)
        else:
            self.graph = None

    # Generic append method based on whatever target is passed in
    def __append(self, target, newValue):
        currentValue = self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY]
        if currentValue == '':
            updatedValue = newValue
        else:
            # Check if new value is already in the current value
            newValuePattern = re.compile('\\b' + newValue + '\\b')
            if re.search(newValuePattern, currentValue):
                updatedValue = currentValue
            else:
                updatedValue = currentValue + '|' + newValue
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = updatedValue

    # Generic replace method based on whatever target is passed in
    def __replace(self, target, newValue):
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = newValue

    # Method to find a node containing a given value
    def FindRelationWithValue(self, valueToFind):
        if self.graph is not None:
            # iterate through all graph nodes
            for node, values in self.graph.nodes.data():
                # If the current Node's value = the value passed in
                if values[CONST_NODE_VALUE_KEY] == valueToFind:
                    return node
        return None


# Relation Graph
class ConditionalGraph(object):
    # Constructor
    def __init__(self, graphNumber):
        self.graphNumber = graphNumber
        if graphNumber is not None:
            self.graph = generateConditionalGraph(self.graphNumber)
        else:
            self.graph = None

    # Generic append method based on whatever target is passed in
    def __append(self, target, newValue):
        currentValue = self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY]
        if currentValue == '':
            updatedValue = newValue
        else:
            # Check if new value is already in the current value
            newValuePattern = re.compile('\\b' + newValue + '\\b')
            if re.search(newValuePattern, currentValue):
                updatedValue = currentValue
            else:
                updatedValue = currentValue + '|' + newValue
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = updatedValue

    # Generic replace method based on whatever target is passed in
    def __replace(self, target, newValue):
        self.graph.nodes(data=True)[target + str(self.graphNumber)][CONST_NODE_VALUE_KEY] = newValue

    # Method to find a node containing a given value
    def FindConditionalWithValue(self, valueToFind):
        if self.graph is not None:
            # iterate through all graph nodes
            for node, values in self.graph.nodes.data():
                # If the current Node's value = the value passed in
                if values[CONST_NODE_VALUE_KEY] == valueToFind:
                    return node
        return None
