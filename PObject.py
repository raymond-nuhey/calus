#!/usr/bin/python3
# pjscicalc: a scientific calculator in python/html/javascript
# Copyright (C) 2021, 2023 John D Lamb
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import mpmath
import formatOutput

## Global value for digits in output
DIGITS = 24 
## Global value for precision of arithmetic
DECIMAL_PRECISION = 50
mpmath.mp.dps = DECIMAL_PRECISION

class PObject:
  "Abstract base class for parser objects"
  def __init__(self,error):
    self.name = None

class PError:
  "Abstract base class for parser error objects"
  def __init__(self,error):
    "Initialise PError"
    self.name = error

intError = PError('Error: not int')
parError = PError('Parenthesis error')
rangeError = PError('Out of range error')

class Numeral(PObject):
  "PObject for numerals"
  def __init__(self,numeral):
    "Initialise Numeral"
    self.name = numeral

zeroNumeral = Numeral('0')
oneNumeral = Numeral('1')
twoNumeral = Numeral('2')
threeNumeral = Numeral('3')
fourNumeral = Numeral('4')
fiveNumeral = Numeral('5')
sixNumeral = Numeral('6')
sevenNumeral = Numeral('7')
eightNumeral = Numeral('8')
nineNumeral = Numeral('9')
decimalNumeral = Numeral('.')
eNumeral = Numeral('e')
minusNumeral = Numeral('-')

class Sto(PObject):
  "PObject for STO"
  def __init__(self):
    "Initialise Sto"
    self.name = 'STO'
    self.value = 0
STOObject = Sto()

class Mplus(PObject):
  "PObject for M+"
  def __init__(self):
    "Initialise Mplus"
    self.name = 'M+'
    self.value = 0
MplusObject = Mplus()

class Mminus(PObject):
  "PObject for M-"
  def __init__(self):
    "Initialise Mminus"
    self.name = 'M-'
    self.value = 0
MminusObject = Mminus()

class Mcl(PObject):
  "PObject for Mcl"
  def __init__(self):
    "Initialise Mclinus"
    self.name = 'Mcl'
    self.value = 0
MclObject = Mcl()

class Container(PObject):
  "Abstract base class for containers (constant doubles)"
  def __init__(self,value):
    self.name = 'dbl'
    self.value = value
  
class Pi(Container):
  "PObject for pi"
  def __init__(self):
    "Initialise pi"
    self.name = 'pi'
    self.value = mpmath.pi
piObject = Pi()

class Ans(Container):
  "PObject for Ans"
  def __init__(self,value):
    "Initialise Ans"
    self.name = 'ANS'
    self.value = value

class Rcl(Container):
  "PObject for Rcl"
  def __init__(self,value):
    "Initialise Rcl"
    self.name = 'RCL'
    self.value = value

class AFunction(PObject):
  "Abstract base class for +/-"
  pass
  
class Add(AFunction):
  "PObject for Add"
  def __init__(self):
    "Initialise plus"
    self.name = '+'
  def fn(self,containerl,containerr):
    dl = containerl.value
    dr = containerr.value
    return Container(dl+dr)
addObject = Add()
  
class Subtract(AFunction):
  "PObject for Subtract"
  def __init__(self):
    "Initialise subtracts"
    self.name = '-'
  def fn(self,containerl,containerr):
    dl = containerl.value
    dr = containerr.value
    return Container(dl-dr)
subtractObject = Subtract()

class DFunction(PObject):
  "Abstract base class for functions with left and right argument"
  pass
  
class E(DFunction):
  "PObject for E"
  def __init__(self):
    "Initialise E"
    self.name = 'E'
  def fn(self,containerl,containerr):
    dl = containerl.value
    dr = containerr.value
    return Container(dl*mpmath.pow(10,dr))
eObject = E()
  
class Power(DFunction):
  "PObject for Power"
  def __init__(self):
    "Initialise Power"
    self.name = '^'
  def fn(self,containerl,containerr):
    dl = containerl.value
    dr = containerr.value
    if dl < 0 and dr != mpmath.nint(dr):
      return rangeError
    return Container(mpmath.power(dl,dr))
powerObject = Power()

class Root(DFunction):
  "PObject for Root"
  def __init__(self):
    "Initialise Root"
    self.name = 'root'
  def fn(self,containerl,containerr):
    dl = mpmath.mpf(1)/containerl.value
    dr = containerr.value
    if dr < 0 and dl != mpmath.nint(dr):
      return rangeError
    return Container(mpmath.power(dr,dl))
rootObject = Root()
  
class Combination(DFunction):
  "PObject for Combination"
  def __init__(self):
    "Initialise Combination"
    self.name = 'C'
  def fn(self,containerl,containerr):
    dl = containerl.value
    dr = containerr.value
    if dl != int(dl) or dr != int(dr):
      return intError;
    return Container(mpmath.binomial(int(dl),int(dr)))
combinationObject = Combination()

class Permutation(DFunction):
  "PObject for Permutation"
  def __init__(self):
    "Initialise Permutation"
    self.name = 'P'
  def fn(self,containerl,containerr):
    dl = containerl.value
    dr = containerr.value
    if dl != int(dl) or dr != int(dr):
      return intError;
    return Container(mpmath.binomial(int(dl),int(dl)-int(dr)))
permutationObject = Permutation()

class LParen(PObject):
  "PObject for ("
  def __init__(self):
    "Initialise LParen"
    self.name = '('
lparenObject = LParen()

class RParen(PObject):
  "PObject for )"
  def __init__(self):
    "Initialise RParen"
    self.name = ')'
rparenObject = RParen()

class RFunction(PObject):
  "Abstract base class for functions with right argument"
  pass
  
class Uplus(RFunction):
  "PObject for +"
  def __init__(self):
    "Initialise Uplus"
    self.name = 'u+'
  def fn(self,container):
    return container
uplusObject = Uplus()

class Uminus(RFunction):
  "PObject for -"
  def __init__(self):
    "Initialise Uminus"
    self.name = 'u-'
  def fn(self,container):
    d = container.value
    return Container(-d)
uminusObject = Uminus()

class SquareRoot(RFunction):
  "PObject for square root"
  def __init__(self):
    "Initialise SquareRoot"
    self.name = 'sqrt'
  def fn(self,container):
    d = container.value
    if d < 0:
      return rangeError
    return Container(mpmath.sqrt(d))
squareRootObject = SquareRoot()

class CubeRoot(RFunction):
  "PObject for cube root"
  def __init__(self):
    "Initialise CubeRoot"
    self.name = 'cbrt'
  def fn(self,container):
    d = container.value
    return Container(mpmath.power(d,mpmath.mpf(1)/mpmath.mpf(3)))
cubeRootObject = CubeRoot()

class Log(RFunction):
  "PObject for log"
  def __init__(self):
    "Initialise Log"
    self.name = 'log'
  def fn(self,container):
    d = container.value
    if d <= 0:
      return rangeError
    return Container(mpmath.log10(d))
logObject = Log()

class Ln(RFunction):
  "PObject for ln"
  def __init__(self):
    "Initialise Ln"
    self.name = 'ln'
  def fn(self,container):
    d = container.value
    if d <= 0:
      return rangeError
    return Container(mpmath.log(d))
lnObject = Ln()

class TenX(RFunction):
  "PObject for 10^x"
  def __init__(self):
    "Initialise TenX"
    self.name = 'tenX'
  def fn(self,container):
    d = container.value
    return Container(mpmath.power(10,d))
tenXObject = TenX()

class Exp(RFunction):
  "PObject for exp"
  def __init__(self):
    "Initialise Exp"
    self.name = 'exp'
  def fn(self,container):
    d = container.value
    return Container(mpmath.exp(d))
expObject = Exp()

class TrigFunction(RFunction):
  "Abstract base class for trig functions"
  pass

class Sin(TrigFunction):
  "PObject for sin"
  def __init__(self):
    "Initialise Sin"
    self.name = 'sin'
  def fn(self,container,scale):
    if 1 == scale:
      d = mpmath.sin(container.value)
    else:
      d = mpmath.sin(mpmath.radians(container.value))
    if mpmath.fabs(d) < mpmath.mpf(1e-50):
      d = mpmath.mpf(0)
    return Container(d)
sinObject = Sin()

class Cos(TrigFunction):
  "PObject for cos"
  def __init__(self):
    "Initialise Cos"
    self.name = 'cos'
  def fn(self,container,scale):
    if 1 == scale:
      d = mpmath.cos(container.value)
    else:
      d = mpmath.cos(mpmath.radians(container.value))
    if mpmath.fabs(d) < mpmath.mpf(1e-50):
      d = mpmath.mpf(0)
    return Container(d)
cosObject = Cos()

class Tan(TrigFunction):
  "PObject for tan"
  def __init__(self):
    "Initialise tan"
    self.name = 'Tan'
  def fn(self,container,scale):
    if 1 == scale:
      d = mpmath.tan(container.value)
    else:
      d = mpmath.tan(mpmath.radians(container.value))
    if mpmath.fabs(d) < mpmath.mpf(1e-50):
      d = mpmath.mpf(0)
    return Container(d)
tanObject = Tan()

class Arcsin(TrigFunction):
  "PObject for sin"
  def __init__(self):
    "Initialise Arcsin"
    self.name = 'ascosin'
  def fn(self,container,scale):
    if container.value > mpmath.mpf(1) or container.value < mpmath.mpf(-1):
      return rangeError
    if 1 == scale:
      d = mpmath.asin(container.value)
    else:
      d = mpmath.degrees(mpmath.asin(container.value))
    if mpmath.fabs(d) < mpmath.mpf(1e-50):
      d = mpmath.mpf(0)
    return Container(d)
arcsinObject = Arcsin()

class Arccos(TrigFunction):
  "PObject for cos"
  def __init__(self):
    "Initialise Arccos"
    self.name = 'acos'
  def fn(self,container,scale):
    if container.value > mpmath.mpf(1) or container.value < mpmath.mpf(-1):
      return rangeError
    if 1 == scale:
      d = mpmath.acos(container.value)
    else:
      d = mpmath.degrees(mpmath.acos(container.value))
    if mpmath.fabs(d) < mpmath.mpf(1e-50):
      d = mpmath.mpf(0)
    return Container(d)
arccosObject = Arccos()

class Arctan(TrigFunction):
  "PObject for arctan"
  def __init__(self):
    "Initialise Arctan"
    self.name = 'atan'
  def fn(self,container,scale):
    if container.value > mpmath.mpf(1) or container.value < mpmath.mpf(-1):
      return rangeError
    if 1 == scale:
      d = mpmath.atan(container.value)
    else:
      d = mpmath.degrees(mpmath.atan(container.value))
    if mpmath.fabs(d) < mpmath.mpf(1e-50):
      d = mpmath.mpf(0)
    return Container(d)
arctanObject = Arctan()

class LFunction(PObject):
  "Abstract base class for functions with left argument"
  pass

class Square(LFunction):
  "PObject for square"
  def __init__(self):
    "Initialise Square"
    self.name = 'square'
  def fn(self,container):
    d = container.value
    return Container(d*d)
squareObject = Square()

class Cube(LFunction):
  "PObject for cube"
  def __init__(self):
    "Initialise Cube"
    self.name = 'cube'
  def fn(self,container):
    d = container.value
    return Container(d*d*d)
cubeObject = Cube()

class Factorial(LFunction):
  "PObject for factorial"
  def __init__(self):
    "Initialise Factorial"
    self.name = '!'
  def fn(self,container):
    d = container.value
    return Container(mpmath.factorial(d))
factorialObject = Factorial()

class Inverse(LFunction):
  "PObject for inverse"
  def __init__(self):
    "Initialise Inverse"
    self.name = 'inv'
  def fn(self,container):
    d = container.value
    return Container(1/d)
inverseObject = Inverse()

class MFunction(PObject):
  "Abstract base class for functions multiplicaion/division"
  pass

class Multiply(MFunction):
  "PObject for *"
  def __init__(self):
    "Initialise Multiply"
    self.name = '*'
  def fn(self,containerl,containerr):
    dl = containerl.value
    dr = containerr.value
    return Container(dl*dr)
multiplyObject = Multiply()

class Divide(MFunction):
  "PObject for /"
  def __init__(self):
    "Initialise Divide"
    self.name = '/'
  def fn(self,containerl,containerr):
    dl = containerl.value
    dr = containerr.value
    return Container(dl/dr)
divideObject = Divide()

##
# Splice a list
##
def splice(myList,index,elements,newElement=None):
  part1 = myList[:index]
  part2 = myList[index+elements:]
  if None == newElement:
    return part1+part2
  else:
    return part1+[newElement]+part2
    
##
# Convert a string from calnulator title to list o PObjects
##
def convertStringToPObjectList(objectString,memory,answer):
  tokens = objectString.split(';')
  pobjects = []
  for token in tokens:
    if '' == token:
      pass
    elif '#0' == token:
      pobjects += [zeroNumeral]
    elif '#1' == token:
      pobjects += [oneNumeral]
    elif '#2' == token:
      pobjects += [twoNumeral]
    elif '#3' == token:
      pobjects += [threeNumeral]
    elif '#4' == token:
      pobjects += [fourNumeral]
    elif '#5' == token:
      pobjects += [fiveNumeral]
    elif '#6' == token:
      pobjects += [sixNumeral]
    elif '#7' == token:
      pobjects += [sevenNumeral]
    elif '#8' == token:
      pobjects += [eightNumeral]
    elif '#9' == token:
      pobjects += [nineNumeral]
    elif '#.' == token:
      pobjects += [decimalNumeral]
    elif '#e' == token:
      pobjects += [eNumeral]
    elif '#-' == token:
      pobjects += [minusNumeral]
    elif 'pi' == token:
      pobjects += [piObject]
    elif 'ANS' == token:
      pobjects += [Ans(answer)]
    elif 'RCL' == token:
      pobjects += [Rcl(memory)]
    elif '+' == token:
      pobjects += [addObject]
    elif '-' == token:
      pobjects += [subtractObject]
    elif 'E' == token:
      pobjects += [eObject]
    elif '^' == token:
      pobjects += [powerObject]
    elif 'C' == token:
      pobjects += [combinationObject]
    elif 'P' == token:
      pobjects += [permutationObject]
    elif 'root' == token:
      pobjects += [rootObject]
    elif '(' == token:
      pobjects += [lparenObject]
    elif ')' == token:
      pobjects += [rparenObject]
    elif 'u+' == token:
      pobjects += [uplusObject]
    elif 'u-' == token:
      pobjects += [uminusObject]
    elif 'sqrt' == token:
      pobjects += [squareRootObject]
    elif 'cbrt' == token:
      pobjects += [cubeRootObject]
    elif 'log' == token:
      pobjects += [logObject]
    elif 'ln' == token:
      pobjects += [lnObject]
    elif 'tenX' == token:
      pobjects += [tenXObject]
    elif 'exp' == token:
      pobjects += [expObject]
    elif 'sin' == token:
      pobjects += [sinObject]
    elif 'cos' == token:
      pobjects += [cosObject]
    elif 'tan' == token:
      pobjects += [tanObject]
    elif 'asin' == token:
      pobjects += [arcsinObject]
    elif 'acos' == token:
      pobjects += [arccosObject]
    elif 'atan' == token:
      pobjects += [arctanObject]
    elif '2' == token:
      pobjects += [squareObject]
    elif '3' == token:
      pobjects += [cubeObject]
    elif '!' == token:
      pobjects += [factorialObject]
    elif 'inv' == token:
      pobjects += [inverseObject]
    elif '*' == token:
      pobjects += [multiplyObject]
    elif '/' == token:
      pobjects += [divideObject]
    elif 'STO' == token:
      pobjects += [STOObject]
    elif 'M+' == token:
      pobjects += [MplusObject]
    elif 'M-' == token:
      pobjects += [MminusObject]
    elif 'MCL' == token:
      pobjects += [MclObject]
    else:
      print('convertStringToPObjectList: \''+token+'\' is not recognised.')
  return pobjects

##
# Convert exponents into a form that can be read directly. Exponents get
# converted early in the process of evaluating an expression.
# @param list A list of tokens to be evaluated.
##
def convertExponentsToNumerals(list):
  i = 0
  while i < len(list):
    obj = list[i];
    if isinstance(obj,E):
      list[i] = eNumeral
      negative = False;
      j = i+1
      while True:
        if not (isinstance(list[j],Add) or isinstance(list[j],Subtract)):
          break
        obj = list[j]
        if isinstance(obj,Subtract):
          # instance of Subtract
          negative = not negative
        # remove regardless whether Add or Subtract
        list = splice(list,i+1,1)
      ## run out of +es and –es
      if negative:
        list = splice(list,i+1,0,minusNumeral)
    # next iteration
    i += 1
  return list

##
# Convert anything that is a Numeral into a Double
# Exponents are also converted implicitly.
# @see Numeral
# @param list A list of tokens to be evaluated.
##
def convertNumerals(list):
  list = convertExponentsToNumerals(list);
  i = 0
  while i < len(list):
    obj = list[i];
    if isinstance(obj,Numeral):
      # find first thing that is not a numeral
      j = i + 1
      while j < len(list) and isinstance(list[j],Numeral):
        j += 1
      # Now [i,j) is a number
      numberString = ''
      for k in range(i,j):
        numberString += list[k].name
      list = splice(list,i,j-i,Container(mpmath.mpmathify(numberString)))
    ## next iteration
    i += 1
  return list

##
# This is where unary plus/minus is handled. Implicitly calls
# convertIs.
# @param list A list of tokens to be evaluated.
##
def convertARFunctions(list):
  # first we must convert Numerals (PiObject/ANS/RCL are already okay)
  list = convertNumerals(list);
  # This time we work right-to-left
  L = len(list)
  if 0 == L:
    return list
  i = L - 1 # list always has at least one element
  while i >= 0:
    a = list[i]
    if isinstance(a,AFunction):
      if 0 == i or not (isinstance(list[i-1],Container) or isinstance(list[i-1],LFunction)):
        # unary ±
        if isinstance(a,Add):
          list = splice(list,i,1,uplusObject)
        elif isinstance(a,Subtract):
          list = splice(list,i,1,uminusObject)
        else:
          print('± error (not unary ±)')
    ## next item
    i -= 1
  return list

##
# Deal with Square and like left functions.
# Calls convertARFunction  first.
# @param list A list of tokens to be evaluated.
#/
def convertLFunctions(list):
  # first we must convert ARFunctions
  list = convertARFunctions(list)
  i = 0
  while i < len(list):
    obj = list[i];
    if isinstance(obj,LFunction):
      d = obj.fn(list[i-1])
      list = splice(list,i-1,2,d)
      i -= 1
    i += 1
  return list

##
# Deal with functions like Power that have both left and right arguments.
# Calls convertLFunctions first.
# @param list A list of tokens to be evaluated.
##
def convertDFunctions(list,scale):
  # first we must convert LFunctions */
  list = convertLFunctions(list)
  i = 0
  while i < len(list):
    if isinstance(list[i],DFunction):
      # Need to evaluate any following RFunctions
      if isinstance(list[i+1],RFunction):
        j = i+1;
        while isinstance(list[j+1],RFunction):
          ++j;
        # j is index of last RFunction
        while j > i:
          if isinstance(list[j],TrigFunction):
            list[j] = list[j].fn(list[j+1],scale)
          else:
            list[j] = list[j].fn(list[j+1])
          list = splice(list,j+1,1);
          --j # next RFunction
      list[i-1] = list[i].fn(list[i-1],list[i+1]);
      list = splice(list,i,2);
    else:
      i += 1
  return list

##
# Deal with functions like SquareRoot that have right argument only.
# Calls convertDFunctions first.
# @param list A list of tokens to be evaluated.
##
def convertRFunctions(list,scale):
  # first we must convert DFunctions
  list = convertDFunctions(list,scale);
  # This time we work right-to-left
  L = len(list)
  if L < 2:
    return list
  i = L-2
  while i > -1:
    o = list[i]
    if isinstance(o,RFunction):
      if isinstance(o,TrigFunction):
        list = splice(list,i,2,o.fn(list[i+1],scale))
      else:
        list = splice(list,i,2,o.fn(list[i+1]))
    i -= 1
  return list

##
# Deal with multiplication and division.
# Calls convertRFunctions first.
# @param list A list of tokens to be evaluated.
##
def convertMFunctions(list,scale):
  # first we must convert RFunctions
  list = convertRFunctions(list,scale)
  L = len(list)
  if L < 3:
    return list
  i = 1
  while i+1 < len(list): # skip first and last
    o = list[i]
    if isinstance(o,MFunction):
      list[i-1] = o.fn(list[i-1],list[i+1]);
      list = splice(list,i,2)
      i -= 1
    i += 1
  return list

##
# Deal with addition and subtraction.
# Calls convertMFunctions first.
# @param list A list of tokens to be evaluated.
##
def convertAFunctions(list,scale):
  # first we must convert MFunctions
  list = convertMFunctions(list,scale)
  L = len(list)
  if L < 1:
    return list
  i = 1
  while i < len(list):
    o = list[i]
    if isinstance(o,AFunction):
      list[i-1] = list[i].fn(list[i-1],list[i+1])
      list = splice(list,i,2)
      i -= 1
    i += 1
  return list

##
# Takes final expression and multiplies all numbers together.
# Calls AFunctions first (and cascades)
# @param list A list of tokens to be evaluated.
##
def convertToProduct(list,scale):
  list = convertAFunctions(list,scale);
  while len(list) > 1:
    list[0] = Container(list[0].value*list[1].value);
    list = splice(list,1,1)
  return list

##
# Tries to strip a pair of parentheses. If it succeeds, the expression in
# parentheses is passed to convertToProduct and so on up the chain
# so that it gets converted to a double.
# Used convertToProduct() to do detailed conversion.
# @return list, True if we managed to strip a pair of parentheses, list, False otherwise
##
def stripParentheses(list,scale):
  lparen = -1;
  rparen = -1;
  L = len(list)
  if 0 == L:
    return list
  i = 0
  while i < L:
    obj = list[i]
    if isinstance(obj,LParen):
      lparen = i
    elif isinstance(obj,RParen):
      rparen = i
      break
    i += 1
  if -1 == lparen and -1 == rparen:
    return list, False
  if -1 == lparen or -1 == rparen:
    list = [parError]
    return list, False
  sublist = list[lparen+1:rparen]
  sublist = convertToProduct(sublist,scale)
  list = splice(list,lparen,rparen-lparen+1)
  for i in range(len(sublist)):
    list = splice(list,lparen+i,0,sublist[i])
  return list, True

##
# This is the main evaluation function. It works by a finding suitable
# subexpressions and calling a cascade of methods to evaluate the expression
# in the correct sequence. Thus the parser works largely by recursion on
# what can be thought of as a tree of PObjects defined by the sequence of
# Parser methods and the PObject hierarchy.
#
# There may be some inconsistency here&mdash;either Parser should store AngleType
# or it doesn&rsquo;t need to store Base.
# It won&rsquo;t cause any errors because we&rsquo;ll
# always get evaluated what was displayed.
#
# @param scale Whether to use radians or degrees
# @return A double or an error if the expression was nonsensical.
#/
def evaluate(list,scale):
  try:
    while True:
      list, rpt = stripParentheses(list,scale)
      if False == rpt:
        break
    list = convertToProduct(list,scale)
    d = list[0]
    return d.value,formatOutput.format(d.value,DIGITS)
    #return d.value,formatOutput.format(d.value,DIGITS)
  except:
    return 'Error','Error'
