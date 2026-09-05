import ast
import astor

with open('FrontEnd/logging_system.py', 'r', encoding='utf-8') as f:
    source = f.read()

tree = ast.parse(source)

classes_to_remove = ['DetailedDataSharingDialog', 'ImprovedGoogleFormsSubmitter', 'ImprovedDataFormatter']

class RemoveClasses(ast.NodeTransformer):
    def visit_ClassDef(self, node):
        if node.name in classes_to_remove:
            return None
        return node

transformer = RemoveClasses()
new_tree = transformer.visit(tree)
ast.fix_missing_locations(new_tree)

new_source = astor.to_source(new_tree)

with open('FrontEnd/services/logging_service.py', 'w', encoding='utf-8') as f:
    f.write(new_source)
