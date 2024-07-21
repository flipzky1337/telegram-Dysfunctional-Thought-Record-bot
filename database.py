import psycopg2

usual_commands = {
    'exist_checking':'SELECT EXISTS(SELECT 1 FROM user_groups WHERE user_id = (%s))',
    'insert':'INSERT INTO user_groups (user_id, group_id) VALUES (%s, %s)'
}


def connect():
    try:
        with psycopg2.connect(host='localhost', database='tj', user='postgres', password='admin') as connection:
            print('Succesfully connected to PG DB')
            return connection
    except (psycopg2.DatabaseError, Exception) as e:
        print(e)


def user_group_storing(connection, user_id, group_id):
