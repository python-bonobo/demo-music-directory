import logging
import mondrian
import psycopg2

POSTGRES_HOST = 'localhost'
POSTGRES_DBNAME = 'mused'
POSTGRES_USER = 'mused'
POSTGRES_PASSWORD = 'mused'
ADMIN_POSTGRES_DBNAME = 'postgres'
ADMIN_POSTGRES_USER = 'postgres'
ADMIN_POSTGRES_PASSWORD = ''

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def _execute(con, sql):
    with con.cursor() as cursor:
        try:
            logger.info('[SQL] {}'.format(sql).strip())
            cursor.execute(sql)
        except psycopg2.ProgrammingError as exc:
            logger.warning('{}: {}'.format(type(exc).__name__, str(exc).strip()))


def drop(con):
    con.set_isolation_level(0)
    _execute(con, 'DROP DATABASE {};'.format(POSTGRES_DBNAME))
    _execute(con, 'DROP ROLE {};'.format(POSTGRES_USER))

def create(con):
    con.set_isolation_level(0)
    _execute(con, 'CREATE ROLE {} WITH LOGIN PASSWORD \'{}\';'.format(POSTGRES_USER, POSTGRES_PASSWORD))
    _execute(con, 'CREATE DATABASE {} WITH OWNER={} TEMPLATE=template0 ENCODING="utf-8";'.format(POSTGRES_DBNAME, POSTGRES_USER))


if __name__ == "__main__":
    mondrian.setup(excepthook=True)
    con = psycopg2.connect(dbname=ADMIN_POSTGRES_DBNAME, user=ADMIN_POSTGRES_USER, host=POSTGRES_HOST, password=ADMIN_POSTGRES_PASSWORD)

    drop(con)
    create(con)



