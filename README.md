Test problem ' ScanFactory'.

Some TODOs for the next refactoring:

1. main.get_urls()
Rewrite as a Python generator, extracting data by portions
2. main.push_to_rules()
Do not upload rules that are already exist in the table (create unique constraint in db?)
3. tree_processing
Functions garbage_subsets() and generate_regexp() do the same calculation sizes for subgroups
--
4. Create tests
5. Format general code as a class

