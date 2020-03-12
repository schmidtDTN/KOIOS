from Constants import *


# Check if current line is a conditional or a header line
def getSymbolLines(DRSLines):
    # Declarations
    symbolLines = {}
    # Iterate through DRS commands
    for index, line in enumerate(DRSLines):
        # If line starts with bracket, it's a header
        if line[0] == CONST_HEADER_LINE_SYMBOL:
            if line == '[]':
                symbolLines.update({index: CONST_JUNK_LINE_TAG })
            else:
                symbolLines.update({index: CONST_HEADER_LINE_TAG})
        # if line is arrow, it's a conditional
        elif line == CONST_CONDITIONAL_LINE_SYMBOL:
            symbolLines.update({index: CONST_CONDITIONAL_LINE_TAG})
        # if line is "QUESTION" then it's the start of a question segment
        elif line == CONST_QUESTION_LINE_SYMBOL:
            symbolLines.update({index: CONST_QUESTION_LINE_TAG})
        # if line is "NOT" then it's the start of a negation segment
        elif line == CONST_NEGATION_LINE_SYMBOL:
            symbolLines.update({index: CONST_NEGATION_LINE_TAG})
        # if line is "MUST" then it's the start of a necessity segment
        elif line == CONST_NECESSITY_LINE_SYMBOL:
            symbolLines.update({index: CONST_NECESSITY_LINE_TAG})
    # print(symbolLines)
    return symbolLines


def categorizeSymbolLines(symbolLines):
    # SymbolLines - check surrounding symbols and set instruction-header/if-header/then-header/question-header
    # accordingly
    symbolLineIndexes = list(symbolLines.keys())
    categorizedSymbolLines = {}
    for symbolIndex, symbolLineNumber in enumerate(symbolLineIndexes):
        # Get symbol and surrounding symbols
        currentSymbol = symbolLines[symbolLineNumber]
        previousSymbol = None
        nextSymbol = None
        # If not first line, then set previous symbol
        if symbolIndex != 0:
            previousSymbolLineNumber = symbolLineIndexes[symbolIndex - 1]
            previousSymbol = symbolLines[previousSymbolLineNumber]
        # If not last line, then set next symbol
        if symbolIndex < (len(symbolLines) - 1):
            nextSymbolLineNumber = symbolLineIndexes[symbolIndex + 1]
            nextSymbol = symbolLines[nextSymbolLineNumber]
        # Categorize headers (ignore rest)
        if currentSymbol == CONST_HEADER_LINE_TAG:
            # First header always = instruction as far as I've been able to see
            if previousSymbol is None:
                categorizedSymbolLines.update({symbolLineNumber: CONST_INSTRUCTION_HEADER_TAG})
            # If previous symbol is "QUESTION", then header is for a question
            if previousSymbol == CONST_QUESTION_LINE_TAG:
                categorizedSymbolLines.update({symbolLineNumber: CONST_QUESTION_HEADER_TAG})
            # if previous symbol is a conditional, then header is for a then part of the conditional
            if previousSymbol == CONST_CONDITIONAL_LINE_TAG:
                categorizedSymbolLines.update({symbolLineNumber: CONST_THEN_HEADER_TAG})
            # if previous symbol is "NOT", then header is for a negation
            if previousSymbol == CONST_NEGATION_LINE_TAG:
                categorizedSymbolLines.update({symbolLineNumber: CONST_NEGATION_HEADER_TAG})
            # if next symbol is a conditional, then header is for an if part of the conditional
            if nextSymbol == CONST_CONDITIONAL_LINE_TAG:
                # if previous symbol is "NOT" and the next symbol is => then this is a negated condition:
                categorizedSymbolLines.update({symbolLineNumber: CONST_IF_HEADER_TAG})
                if previousSymbol == CONST_NEGATION_LINE_TAG:
                    categorizedSymbolLines.update({symbolLineNumber: CONST_IF_NEGATION_HEADER_TAG})
        else:
            categorizedSymbolLines.update({symbolLineNumber: currentSymbol})
    return categorizedSymbolLines


# Categorize each variable in the DRS program with a type (instruction, if, then, question)
def categorizeVariables(DRSLines, categorizedSymbolLines):
    variablesAndTypes = {}
    # Iterate through Symbol Lines in order to extract each variable from the headers and its associated type
    for symbolLineNumber, symbolLineType in categorizedSymbolLines.items():
        # check if header type
        if CONST_HEADER_LINE_TAG in symbolLineType:
            # get current line
            currentSymbolLine = DRSLines[symbolLineNumber]
            # strip brackets
            currentSymbolLine = currentSymbolLine.replace('[', '')
            currentSymbolLine = currentSymbolLine.replace(']', '')
            # Get list of variables contained in header
            currentTargetVariables = currentSymbolLine.split(',')
            # Get current type of the header by stripping the header part of the tag and leaving the type
            currentHeaderType = symbolLineType.split('-header')[0]
            # Assign each variable in the current line to have the associated type with the header
            for variable in currentTargetVariables:
                variablesAndTypes.update({variable: currentHeaderType})
    return variablesAndTypes


# Assign a type (instruction, if, then, question) to each line of the DRS instructions in order to easily check
# line-type during processing
def categorizeDRSLines(DRSLines, symbolLines):
    categorizedDRSLines = {}
    # get categorization of each symbol line
    categorizedSymbolLines = categorizeSymbolLines(symbolLines)
    # Get categorizations of each variable
    variablesAndTypes = categorizeVariables(DRSLines, categorizedSymbolLines)
    # Iterate through DRSLines
    for index, line in enumerate(DRSLines):
        # If current line is in one of the symbol lines, give it the exact same type as it already has
        if index in categorizedSymbolLines.keys():
            currentLineType = categorizedSymbolLines.get(index)
            categorizedDRSLines.update({index: currentLineType})
        # otherwise, it's an instruction - check its reference variable and assign the associated type to the line
        else:
            # Get the contents of this given instruction
            predicateContents = line.split('(', 1)[1]
            # Get the reference variable of the instruction
            predicateReferenceVariable = predicateContents.split(',', 1)[0]
            # Get the type associated with this variable
            currentInstructionType = variablesAndTypes.get(predicateReferenceVariable)
            categorizedDRSLines.update({index: currentInstructionType})
    return categorizedDRSLines
