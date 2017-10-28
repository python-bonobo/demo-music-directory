Music Directory - Bonobo ETL Demo
=================================

Bonobo ETL demo from Pycon.DE talk, using Django2, DBPedia and SPARQL.

Prerequisites and installation
::::::::::::::::::::::::::::::

You need the "bleeding edge" version of bonobo to run this demo.

.. code-block:: shell-session

    pip install git+https://github.com/python-bonobo/bonobo.git@develop#egg=bonobo
    
Read more about installation options: http://docs.bonobo-project.org/en/master/install.html

Application content
:::::::::::::::::::

This demo contains a django2 project, with one management task. All five first commits in the 
repository matches the 5 steps of my talk in Karlsruhe, so you can replay every step by running 
`git rebase -i --root`, setting all commits to `edit` and use `git rebase --continue` to advance 
to the next step.

You'll need a postgresql server running, starting from step 3.

To apply database migrations, just run `./manage.py migrate`.

To run the webserver, run `./manage.py runserver`.

To run the importer from dbpedia, run `./manage.py import_dbpedia`.

Slides from the talk
::::::::::::::::::::

https://www.slideshare.net/hartym/simple-data-engineering-in-python-35-pyconde-2017-karlsruhe-bonobo-etl
