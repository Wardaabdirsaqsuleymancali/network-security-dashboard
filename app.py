import re
import streamlit as st

# ==========================================
# PHASE 1: LEXICAL ANALYSIS (SCANNER)
# ==========================================
TOKEN_SPECIFICATION = [
    ('FLOAT_NUM', r'\d+\.\d+'),          # Floating-point numbers
    ('INT_NUM',   r'\d+'),               # Integer numbers
    ('KEYWORD',   r'\b(int|float|if|else|while|print)\b'), # Keywords
    ('ID',        r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),          # Identifiers
    ('ASSIGN',    r'='),                 # Assignment operator
    ('OP',        r'[+\-*/%]|<=|>=|==|!=|<|>'), # Operators (Arithmetic & Relational)
    ('DELIMITER', r'[;{}()]'),           # Delimiters
    ('SKIP',      r'[ \t\n]+'),          # Whitespace and newlines
    ('MISMATCH',  r'.'),                 # Invalid Token
]

class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.errors = []

    def tokenize(self):
        regex_parts = [f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECIFICATION]
        master_regex = re.compile('|'.join(regex_parts))
        
        line_num = 1
        for match in master_regex.finditer(self.code):
            token_type = match.lastgroup
            token_value = match.group(token_type)
            
            if token_type == 'SKIP':
                if '\n' in token_value:
                    line_num += token_value.count('\n')
                continue
            elif token_type == 'MISMATCH':
                self.errors.append(f"Lexical Error: Invalid Token '{token_value}' on line {line_num}")
                self.tokens.append(('INVALID', token_value, line_num))
            else:
                self.tokens.append((token_type, token_value, line_num))
        return self.tokens, self.errors


# ==========================================
# PHASE 3: SYMBOL TABLE & PHASE 4: SEMANTIC ANALYSIS
# ==========================================
class SymbolTable:
    def __init__(self):
        self.table = {}
        self.errors = []

    def declare(self, name, data_type, line):
        if name in self.table:
            self.errors.append(f"Semantic Error: Duplicate declaration of variable '{name}' on line {line}")
            return False
        self.table[name] = {'type': data_type, 'value': None}
        return True

    def lookup(self, name):
        return self.table.get(name, None)

    def update_value(self, name, value):
        if name in self.table:
            self.table[name]['value'] = value


# ==========================================
# PHASE 2: SYNTAX ANALYSIS (PARSER) & SEMANTIC CHECKS
# ==========================================
class Parser:
    def __init__(self, tokens, symbol_table):
        self.tokens = [t for t in tokens if t[0] != 'INVALID']
        self.symbol_table = symbol_table
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
        self.tac_instructions = []
        self.temp_counter = 0
        self.syntax_errors = []
        self.last_seen_line = 1  # Waxay kaydinaysaa line-kii ugu dambeeyay ee la dhex maray

    def advance(self):
        # Kahor intaanan hore u socon, kaydi line-ka hadda la taagan yahay
        if self.current_token:
            self.last_seen_line = self.current_token[2]
            
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def new_temp(self):
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def error(self, message):
        # Haddii koodhkii dhammaaday (None), isticmaal line-kii u dambeeyay ee la kaydiyay
        if self.current_token:
            line = self.current_token[2]
        else:
            line = self.last_seen_line
        self.syntax_errors.append(f"Syntax Error: {message} on line {line}")

    def parse(self):
        while self.current_token is not None:
            self.statement()

    def statement(self):
        if self.current_token and self.current_token[0] == 'KEYWORD' and self.current_token[1] in ['int', 'float']:
            data_type = self.current_token[1]
            self.advance()
            
            if self.current_token and self.current_token[0] == 'ID':
                var_name = self.current_token[1]
                self.symbol_table.declare(var_name, data_type, self.current_token[2])
                self.advance()
                
                if self.current_token and self.current_token[0] == 'ASSIGN':
                    self.advance()
                    expr_val, expr_type = self.expression()
                    
                    if data_type != expr_type:
                        self.symbol_table.errors.append(f"Semantic Error: Type mismatch. Cannot assign {expr_type} to variable '{var_name}' of type {data_type} on line {self.current_token[2]}")
                    else:
                        self.symbol_table.update_value(var_name, expr_val)
                        self.tac_instructions.append(f"{var_name} = {expr_val}")
                
                if self.current_token and self.current_token[1] == ';':
                    self.advance()
                else:
                    self.error("Expected ';'")
            else:
                self.error("Expected variable identifier")

        elif self.current_token and self.current_token[0] == 'ID':
            var_name = self.current_token[1]
            var_info = self.symbol_table.lookup(var_name)
            
            if not var_info:
                self.symbol_table.errors.append(f"Semantic Error: Variable '{var_name}' is not declared on line {self.current_token[2]}")
                var_type = 'unknown'
            else:
                var_type = var_info['type']
                
            self.advance()
            
            if self.current_token and self.current_token[0] == 'ASSIGN':
                self.advance()
                expr_val, expr_type = self.expression()
                
                if var_type != 'unknown' and var_type != expr_type:
                     self.symbol_table.errors.append(f"Semantic Error: Type mismatch. Cannot assign {expr_type} to variable '{var_name}' of type {var_type} on line {self.current_token[2]}")
                else:
                    self.symbol_table.update_value(var_name, expr_val)
                    self.tac_instructions.append(f"{var_name} = {expr_val}")
                
                if self.current_token and self.current_token[1] == ';':
                    self.advance()
                else:
                    self.error("Expected ';'")
            else:
                self.error("Expected '=' operator")

        elif self.current_token and self.current_token[1] == 'if':
            self.advance()
            if self.current_token and self.current_token[1] == '(':
                self.advance()
                cond, _ = self.expression()
                if self.current_token and self.current_token[1] == ')':
                    self.advance()
                    
                    self.tac_instructions.append(f"if {cond} goto L1")
                    self.tac_instructions.append("goto L2")
                    self.tac_instructions.append("L1:")
                    
                    if self.current_token and self.current_token[1] == '{':
                        self.advance()
                        self.statement()
                        if self.current_token and self.current_token[1] == '}':
                            self.advance()
                        else:
                            self.error("Expected '}'")
                    else:
                        self.statement()
                        
                    self.tac_instructions.append("L2:")
                else:
                    self.error("Expected ')'")
            else:
                self.error("Expected '('")

        elif self.current_token and self.current_token[1] == 'print':
            self.advance()
            if self.current_token and self.current_token[1] == '(':
                self.advance()
                if self.current_token and self.current_token[0] == 'ID':
                    var_name = self.current_token[1]
                    if not self.symbol_table.lookup(var_name):
                        self.symbol_table.errors.append(f"Semantic Error: Cannot print undeclared variable '{var_name}' on line {self.current_token[2]}")
                    
                    self.tac_instructions.append(f"print {var_name}")
                    self.advance()
                    if self.current_token and self.current_token[1] == ')':
                        self.advance()
                        if self.current_token and self.current_token[1] == ';':
                            self.advance()
                        else:
                            self.error("Expected ';'")
                    else:
                        self.error("Expected ')'")
                else:
                    self.error("Expected identifier inside print")
            else:
                self.error("Expected '('")
        else:
            self.advance()

    def expression(self):
        left, left_type = self.term()
        
        while self.current_token and self.current_token[0] in ['OP', 'ASSIGN']:
            op = self.current_token[1]
            self.advance()
            right, right_type = self.term()
            
            temp = self.new_temp()
            self.tac_instructions.append(f"{temp} = {left} {op} {right}")
            left = temp
            
            if left_type == 'float' or right_type == 'float':
                left_type = 'float'
            else:
                left_type = 'int'
                
        return left, left_type

    def term(self):
        token = self.current_token
        if token:
            if token[0] == 'INT_NUM':
                self.advance()
                return token[1], 'int'
            elif token[0] == 'FLOAT_NUM':
                self.advance()
                return token[1], 'float'
            elif token[0] == 'ID':
                var_info = self.symbol_table.lookup(token[1])
                var_type = var_info['type'] if var_info else 'unknown'
                self.advance()
                return token[1], var_type
        return "0", 'int'


# ==========================================
# PHASE 6: CODE OPTIMIZATION
# ==========================================
class Optimizer:
    def __init__(self, tac_instructions):
        self.tac = tac_instructions

    def optimize(self):
        optimized_tac = []
        constants = {}

        for line in self.tac:
            match = re.match(r'(\w+)\s*=\s*(\d+)\s*([+\-*/%])\s*(\d+)', line)
            if match:
                target, val1, op, val2 = match.groups()
                result = eval(f"{val1} {op} {val2}")
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                line = f"{target} = {result}"
                constants[target] = str(result)

            for var, val in list(constants.items()):
                if '=' in line:
                    parts = line.split('=')
                    right_side = parts[1].strip()
                    if right_side == var:
                        line = f"{parts[0].strip()} = {val}"
                        constants[parts[0].strip()] = val

            optimized_tac.append(line)
        return optimized_tac


# ==========================================
# PHASE 7: TARGET CODE GENERATION (ASSEMBLY)
# ==========================================
class AssemblyGenerator:
    def __init__(self, tac_instructions):
        self.tac = tac_instructions
        self.assembly = []

    def generate(self):
        self.assembly.append(".data")
        self.assembly.append(".text")
        self.assembly.append(".globl main")
        self.assembly.append("main:")
        
        for line in self.tac:
            if ":" in line:
                self.assembly.append(line)
                continue
            
            if "if" in line and "goto" in line:
                parts = line.split()
                cond_var = parts[1]
                label = parts[3]
                self.assembly.append(f"    CMP {cond_var}, 0")
                self.assembly.append(f"    JG {label}")
                continue
                
            if "goto" in line:
                label = line.split()[1]
                self.assembly.append(f"    JMP {label}")
                continue

            if "print" in line:
                var = line.split()[1]
                self.assembly.append(f"    PRINT {var}")
                continue

            parts = line.split('=')
            if len(parts) == 2:
                target = parts[0].strip()
                expr = parts[1].strip().split()
                
                if len(expr) == 1:
                    val = expr[0]
                    self.assembly.append(f"    MOV {target}, {val}")
                elif len(expr) == 3:
                    op1, op, op2 = expr
                    self.assembly.append(f"    MOV R1, {op1}")
                    if op == '+':
                        self.assembly.append(f"    ADD R1, {op2}")
                    elif op == '-':
                        self.assembly.append(f"    SUB R1, {op2}")
                    elif op == '*':
                        self.assembly.append(f"    MUL R1, {op2}")
                    elif op == '/':
                        self.assembly.append(f"    DIV R1, {op2}")
                    elif op == '>':
                        self.assembly.append(f"    CMP R1, {op2}")
                    self.assembly.append(f"    MOV {target}, R1")
                    
        return self.assembly


# ==========================================
# STREAMLIT INTERFACE
# ==========================================
st.set_page_config(page_title="Mini Compiler Web IDE", layout="wide")

st.title("🖥️ Mini Compiler Web IDE")


col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Input Program")
    default_code = """int a = 10;
int b = 20;
int c;
c = a + b;
if (c > 20) {
    print(c);
}"""
    user_code = st.text_area("Ku qor koodhkaaga halkan:", value=default_code, height=250)
    compile_btn = st.button("🚀 Compile & Run", type="primary")

if compile_btn:
    # 1. Lexical Analysis
    lexer = Lexer(user_code)
    tokens, lex_errors = lexer.tokenize()
    
    # 2. Syntax & Semantic Table Setup
    sym_table = SymbolTable()
    parser = Parser(tokens, sym_table)
    parser.parse()
    
    with col2:
        st.subheader("🚦 Compilation Outputs")
        
        # Sifaynta Errors-ka haddii ay jiraan
        all_errors = lex_errors + parser.syntax_errors + sym_table.errors
        if all_errors:
            for error in all_errors:
                st.error(error)
        else:
            st.success("🎉 Compilation Successful! No errors found.")

        # Tab-yo loogu talagalay Output kasta
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔍 Tokens (Lexer)", 
            "📊 Symbol Table", 
            "⚙️ TAC", 
            "⚡ Optimized TAC", 
            "💾 Assembly (Target Code)"
        ])
        
        with tab1:
            st.write("### Lexical Analysis Tokens")
            st.table([{"Lexeme": t[1], "Token Type": t[0], "Line": t[2]} for t in tokens])
            
        with tab2:
            st.write("### Active Symbol Table")
            table_data = []
            for name, info in sym_table.table.items():
                table_data.append({"Variable": name, "Type": info["type"], "Value": str(info["value"])})
            if table_data:
                st.table(table_data)
            else:
                st.info("Symbol Table is empty.")
                
        with tab3:
            st.write("### Intermediate Code (Three-Address Code)")
            if parser.tac_instructions:
                st.code("\n".join(parser.tac_instructions), language="python")
            else:
                st.info("No TAC generated.")
                
        with tab4:
            st.write("### Optimized TAC (Propagation & Folding)")
            optimizer = Optimizer(parser.tac_instructions)
            optimized_tac = optimizer.optimize()
            if optimized_tac:
                st.code("\n".join(optimized_tac), language="python")
            else:
                st.info("No optimized TAC available.")
                
        with tab5:
            st.write("### Target Assembly-Like Code")
            asm_gen = AssemblyGenerator(optimized_tac)
            assembly_code = asm_gen.generate()
            if assembly_code:
                st.code("\n".join(assembly_code), language="x86asm")
            else:
                st.info("No assembly code generated.")