import pymysql

def get_conn():
    conn = pymysql.connect(
            host = "127.18.0.1",
            port = 53306,
            user = 'mnist',
            passwd = '1234',
            db = 'mnistdb',
            cursorclass=pymysql.cursors.DictCursor)

    return conn

def select(query: str, size = -1):
  conn = get_conn()
  with conn:
      with conn.cursor() as cursor:
          cursor.execute(query)
          result = cursor.fetchmany(size)

  return result

def dml(sql, *values):
  conn = get_conn()

  with conn:
    with conn.cursor() as cursor:
        cursor.execute(sql, values)
        conn.commit()
        return cursor.rowcount
