import os.path as op


with open(op.join(op.dirname(__file__), 'models.txt'), 'w') as f:
        # Read the file and print the content
        f.write(repr(__models__))

for model in __models__:
    print(model)