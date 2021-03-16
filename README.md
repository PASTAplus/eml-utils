# EML utilities

## Aggregate queries  

This is a set of utilities that enables simple aggregate queries against an arbitrarily large collection of EML XML documents. It is designed to answer questions about how the various branches and nodes in the EML docs are used for the given collection of docs. The tools assume that the documents have already been successfully validated against an EML XSD schema corresponding to the version declared in each doc.

The set of EML docs to query must be available in the local filesystem. The utilities search a provided directory path recursively for the docs. It does not modify the documents, or the directory tree. Intermedite files containing statistics collected from the EML docs are created in the directory in which the utilities are located.

### PyCharm configuration

By default, the EML document root dir is in the root of the project dir. To prevent PyCharm from attempting to index the documents, and crashing when it runs out of memory, add the directory name in the PyCharm File Type settings (`File > Settings > File Types > Ignored Files and Folders`). It is not sufficient to mark the directory as Excluded in the Project tool window (`Project > Mark Directory as > Excluded`).


[comment]: <> (START GENERATED)

# mk_all_stats.py

```text
usage: mk_all_stats.py [-h]

Create a set of predefined aggregation files concurrently.

Configured directly in the source.

optional arguments:
  -h, --help  show this help message and exit

```

# mk_sample_symlinks.py

```text
usage: mk_sample_symlinks.py [-h] [--sample-count SAMPLE_COUNT]
                             [--eml-root path] [--sample-root SAMPLE_ROOT]
                             [--debug]

Create set of sample EML documents.

This creates a set of symlinks into a directory tree holding EML documents. The EML
documents to which the symlinks are created, are selected randomly from the full set of
docs available in the tree.

The directory in which the symlinks are created can then be used instead of the full
tree when it's sufficient to process only a randomly selected subset instead of the full
collection of EML docs.

The symlinks are created as relative if possible. Relative symlinks will not break if
they are in the same subtree, and the whole subtree is moved to another location.

optional arguments:
  -h, --help            show this help message and exit
  --sample-count SAMPLE_COUNT
                        Number of symlinks to create (default: 100)
  --eml-root path       Path to root of directory tree to search for EML docs
                        (extension must be '.xml') (default:
                        /home/dahl/dev/dex/eml-utils/__all_eml)
  --sample-root SAMPLE_ROOT
                        Directory in which to create the symlinks. Created if
                        it does not exist (default: /home/dahl/dev/dex/eml-
                        utils/samples)
  --debug               Debug level logging (default: False)

```

# mk_stats.py

```text
usage: mk_stats.py [-h] [--eml-root path] [--debug] pickle xpath

Create an intermediate file containing statistics for a collection of EML docs.

The tool applies an XPath to each of the EML docs in the collection and generates some
basic aggregates, including the unique strings and counts of occurences for each of the
matched elements. The result is written to an intermedia file which is used later by
another tool to further filter the data and print final results.

As the intermedia file is expensive to create for large collections of EML doc, we store
them with the utilities themselves, instead of in /tmp (which is not persistent across
reboots).

positional arguments:
  pickle           Stats pickle file
  xpath            Selection for the elements to track

optional arguments:
  -h, --help       show this help message and exit
  --eml-root path  Path to root of directory tree to search for EML docs
                   (extension must be '.xml') (default:
                   /home/dahl/dev/dex/eml-utils/__all_eml)
  --debug          Debug level logging (default: False)

```

# pprint_stats.py

```text
usage: pprint_stats.py [-h] [--values VALUES] [--occurences OCCURENCES]
                       [--length LENGTH] [--debug]
                       pickle

Filter and pretty-print aggregated query results

This reads aggregated query results from an intermediate file created by another tool,
applies simple filters as defined by the command line parameters, and pretty prints the
results. Since it works against previously created aggregations, it enables filters to
be quickly checked and adjusted when examining the results.

positional arguments:
  pickle                Stats pickle file

optional arguments:
  -h, --help            show this help message and exit
  --values VALUES       Only print elements with at least this number of
                        unique values (default: 0)
  --occurences OCCURENCES
                        Only print values with at least this number of
                        occurences (default: 0)
  --length LENGTH       Only print values that are shorter than this (default:
                        100)
  --debug               Debug level logging (default: False)

```

# xpath.py

```text
usage: xpath.py [-h] [--only-text] [--debug] xpath path

Apply an XPath to an EML doc and list the matched elements.

This tool is based on lxml, which is also the library we use in the tool that generates
aggregates from the full collection of EML docs. Though XPath is standardized, there are
many versions of the spec, and each implementation has its own idiosyncrazies. Using
this (or another lxml based tool) should guarantee that the results match those obtained
by the aggregation tool, and so is a good way to create and check the queries before
using them in lengthy aggregations.

positional arguments:
  xpath        Selection for the elements to track
  path         Path to EML doc to which the xpath will be apply

optional arguments:
  -h, --help   show this help message and exit
  --only-text  Only print elements which have text content (default: False)
  --debug      Debug level logging (default: False)

```
