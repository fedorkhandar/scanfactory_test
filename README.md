# Test problem ' ScanFactory'.
An app that 
1. reads from SQLite data from the table 'domains' (name, project_id)
2. analyzes the set of domain names for every project_id
3. generates regular expressions, filtering "garbage" domain names
4. writes generated regexps to the table 'rules' (project_id, regexp)

Main idea:
Let's consider as "garbage" such domain names that:
1) are repeated (more than 1 occurrence of the same length);
2) have no children (subdomains).

--
## Some TODOs for the future refactoring:

1. main.get_urls()
Rewrite as a Python generator, extracting data by portions
2. main.push_to_rules()
Do not upload rules that are already exist in the table (create unique constraint in db?)
3. tree_processing
Functions garbage_subsets() and generate_regexp() do the same calculation sizes for subgroups
--
4. Create tests
5. Format general code as a class

