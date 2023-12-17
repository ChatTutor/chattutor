import pymysql
import uuid
import datetime


class MessageSchema:
    mes_id = ""
    role = ""
    content = ""
    chat_key = ""
    clear_number = 0
    time_created = ""

    def convert_to_dictionary(self):
        return {
            "mes_id": self.mes_id,
            "role": self.role,
            "content": self.content,
            "chat_key": self.chat_key,
            "clear_number": self.clear_number,
            "time_created": self.clear_number,
        }


class ChatSchema:
    chat_id = ""

    def convert_to_dictionary(self):
        return {"chat_id": self.chat_id}


class MessageDB:
    host = ""
    user = ""
    password = ""
    db = ""
    statisticsdb = ""

    # Only for deleting the db when you first access the site. Can be used for debugging
    presetTables1 = """
        DROP TABLE IF EXISTS lchats
    """
    # only for deleting the db when you first access the site. Can be used for debugging
    presetTables2 = """
        DROP TABLE IF EXISTS lmessages
    """

    chats_table_Sql = """
    CREATE TABLE IF NOT EXISTS lchats (
        chat_id varchar(100) PRIMARY KEY
        )"""

    messages_table_Sql = """
    CREATE TABLE IF NOT EXISTS lmessages (
        mes_id varchar(100) PRIMARY KEY,
        role text NOT NULL,
        content text NOT NULL,
        chat_key varchar(100) NOT NULL,
        clear_number integer NOT NULL,
        time_created text NOT NULL,
        FOREIGN KEY (chat_key) REFERENCES lchats (chat_id)
        )"""

    create_course_name = """
    CREATE TABLE IF NOT EXISTS lcourses (
        course_id varchar(250) PRIMARY KEY,
        name text NOT NULL,
        proffessor text not null,
        mainpage text not null,
        collectionname text not null
        )"""

    create_section_name = """
        CREATE TABLE IF NOT EXISTS lsections (
            section_id varchar(250) PRIMARY KEY,
            pulling_from text not null
            )"""

    create_relationship_between_sections_and_courses = """
        CREATE TABLE IF NOT EXISTS rsectionscourses (
            section_id varchar(250) not null ,
            course_id varchar(250) not null,
            FOREIGN KEY (section_id) REFERENCES lsections(section_id),
            FOREIGN KEY (course_id) REFERENCES lcourses(course_id),
            UNIQUE (section_id, course_id)
            )"""
            
    user_table_Sql = """
        CREATE TABLE IF NOT EXISTS lusers (
            username varchar(100) PRIMARY KEY,
            email varchar(100),
            password varchar(100),
        )
        """

    relationship_users_courses = """
        CREATE TABLE IF NOT EXISTS ruserscourses (
            username varchar(250) not null ,
            course_id varchar(250) not null,
            FOREIGN KEY (username) REFERENCES lusers(username),
            FOREIGN KEY (course_id) REFERENCES lcourses(course_id),
            UNIQUE (username, course_id)
        )
    """


    alter_section_Table = """
        ALTER TABLE lsections
        MODIFY sectionurl VARCHAR(256);
    """

<<<<<<< HEAD

=======
>>>>>>> origin/beta-main
    def __init__(self, host, user, password, database, statistics_database):
        self.host = host
        self.user = user
        self.password = password
        self.db = database
        self.statisticsdb = statistics_database
        
    def insert_user(self, user):
        with self.connect_to_messages_database() as con:
            cur = con.cursor()
<<<<<<< HEAD
            # add type too.*args.*args.*args.*args.*args.*args.*args.*args.*args.*args.*args.*args.*args.*args.*args.*args.*args.*args.*args..*args.*args.
            print(f"INSERT IGNORE INTO lusers (username, email, password, user_type) VALUES ('{user.username}', '{user.email}', '{user.password_hash.decode('utf-8') }', '{user.user_type}')")
            cur.execute(f"INSERT IGNORE INTO lusers (username, email, password, user_type) VALUES ('{user.username}', '{user.email}', '{user.password_hash.decode('utf-8') }', '{user.user_type}')")
=======
            print(f"INSERT IGNORE INTO lusers (username, email, password) VALUES ('{user.username}', '{user.email}', '{user.password_hash.decode('utf-8') }')")
            cur.execute(f"INSERT IGNORE INTO lusers (username, email, password) VALUES ('{user.username}', '{user.email}', '{user.password_hash.decode('utf-8') }')")
>>>>>>> origin/beta-main
            con.commit()
            
    def get_user(self, username):
        with self.connect_to_messages_database() as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM lusers WHERE username = '{username}'")
            users = cur.fetchall()
            return users
        
    def insert_user_to_course(self, username, course_id):
        with self.connect_to_messages_database() as con:
            cur = con.cursor()
            cur.execute(f"INSERT INTO ruserscourses (username, course_id) VALUES ('{username}', '{course_id}') ON DUPLICATE KEY UPDATE username='{username}', course_id='{course_id}'")
            con.commit()
            
    def get_user_courses(self, username):
        with self.connect_to_messages_database() as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM lcourses WHERE course_id IN (SELECT course_id FROM ruserscourses WHERE username = '{username}')")
            courses = cur.fetchall()
            return courses
    
    def get_courses_sections(self, course_id):
        with self.connect_to_messages_database() as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM lsections WHERE section_id IN (SELECT section_id FROM rsectionscourses WHERE course_id = '{course_id}')")
            sections = cur.fetchall()
            print(sections)
            return sections
<<<<<<< HEAD


=======


>>>>>>> origin/beta-main
    def get_courses_sections_format(self, course_id):
        with self.connect_to_messages_database() as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM lsections WHERE section_id IN (SELECT section_id FROM rsectionscourses WHERE course_id = '{course_id}')")
            sections = cur.fetchall()
<<<<<<< HEAD
            cur.execute(f"SELECT name FROM lcourses WHERE course_id='{course_id}'")
            names = cur.fetchall()
=======


            cur.execute(f"SELECT name FROM lcourses WHERE course_id='{course_id}'")
            names = cur.fetchall()

            # print(names)
            # print(sections)

>>>>>>> origin/beta-main
            dic = [{
                'section_id': section['section_id'],
                'course_id': course_id,
                'section_url': section['sectionurl'],
                'course_chroma_collection': names[0]['name']
            } for section in sections]

            return dic
    
    def connect_to_messages_database(self):
        """Function that connects to the database"""
        connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            db=self.db,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

        return connection

    def connect_to_statistics_database(self):
        connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            db=self.statisticsdb,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

        return connection

    def initialize_ldatabase(self):
        """Creates the tables if they don't exist"""
        con = self.connect_to_messages_database()
        cur = con.cursor()
        cur.execute(self.chats_table_Sql)
        cur.execute(self.messages_table_Sql)
        cur.execute(self.create_course_name)
        cur.execute(self.create_section_name)
        cur.execute(self.create_relationship_between_sections_and_courses)
        con.commit()
<<<<<<< HEAD

=======
>>>>>>> origin/beta-main

    def insert_message(self, a_message):
        """This inserts a message into the sqlite3 database. the message must be sent as a dictionary"""
        with self.connect_to_messages_database() as con:
            cur = con.cursor()
            role = a_message["role"]
            content = a_message["content"]
            chat_key = a_message["chat"]
            clear_number = a_message["clear_number"]
            time_created = a_message["time_created"]
            insert_format_lmessages = f"INSERT INTO lmessages (mes_id ,role, content, chat_key, clear_number, time_created) VALUES ('{uuid.uuid4()}','{role}', %s, '{chat_key}', {clear_number}, '{time_created}')"
            cur.execute(insert_format_lmessages, (content,))
            con.commit()

    def insert_chat(self, chat_key):
        with self.connect_to_messages_database() as con:
            cur = con.cursor()
            insert_format_lchats = ""
            cur.execute(f"INSERT IGNORE INTO lchats (chat_id) VALUES ('{chat_key}')")
            con.commit()


    def insert_course(self, course_id, name, proffessor, mainpage, collectionname):
        with self.connect_to_messages_database() as con:
            cur = con.cursor()
            cur.execute(f"INSERT INTO lcourses (course_id, name, proffessor, mainpage, collectionname) VALUES ('{course_id}', '{name}', '{proffessor}', '{mainpage}', '{collectionname}') ON DUPLICATE KEY UPDATE course_id='{course_id}', name='{name}', proffessor='{proffessor}', mainpage='{mainpage}', collectionname='{collectionname}'")
            con.commit()

    def insert_section(self, section_id, pulling_from, sectionurl):
        with self.connect_to_messages_database() as con:
            cur = con.cursor()
            cur.execute(f"INSERT INTO lsections (section_id, pulling_from, sectionurl) VALUES ('{section_id}', '{pulling_from}', '{sectionurl}') ON DUPLICATE KEY UPDATE section_id='{section_id}', pulling_from='{pulling_from}', sectionurl='{sectionurl}'")

            con.commit()

    def establish_course_section_relationship(self, section_id, course_id):
        with self.connect_to_messages_database() as con:
            cur = con.cursor()
            cur.execute(f"INSERT INTO rsectionscourses (section_id, course_id) VALUES ('{section_id}', '{course_id}') ON DUPLICATE KEY UPDATE section_id='{section_id}', course_id='{course_id}'")
            con.commit()

    def update_section_add_fromdoc(self, section_id, from_doc):
        with self.connect_to_messages_database() as con:
            cur = con.cursor()
            cur.execute(f"UPDATE lsections SET pulling_from = concat(pulling_from, '{'$'+from_doc}') WHERE section_id = '{section_id}'")
            con.commit()

    def execute_sql(self, sqlexec, commit=True):
        with self.connect_to_messages_database() as con:
            cur = con.cursor()
            response = cur.execute(sqlexec)
            messages_arr = cur.fetchall()
            if commit:
                con.commit()
            return messages_arr
        

    def insert_config(self, user: str, course_id: str, course_url: str, run_locally: int, test_mode: int, is_static: int, build_with: str, server_port: int, chattutor_server: str, token_id: str, use_as_default: int):
        with self.connect_to_messages_database() as con:
            cur = con.cursor()

            """
            user varchar(250) not null ,
            course_id varchar(250) not null,
            course_url varchar(250) not null,
            run_locally integer,
            test_mode integer,
            is_static integer,
            built_with varchar(250),
            server_port integer,
            chattutor_server varchar(250),
            token_id varchar(230) PRIMARY KEY,
            use_as_default integer
            """
            print(f"""INSERT INTO lconfigstokens (user, course_id, course_url, run_locally, test_mode, is_static, built_with, server_port, chattutor_server, token_id, use_as_default)
                            VALUES ('{user}', '{course_id}', '{course_url}', {run_locally}, {test_mode}, {is_static}, '{build_with}', {server_port}, '{chattutor_server}', '{token_id}', {use_as_default}) 
                            ON DUPLICATE KEY UPDATE user='{user}', course_id='{course_id}', course_url='{course_url}',
                                                    run_locally={run_locally}, test_mode={test_mode}, is_static={is_static}, built_with='{build_with}', server_port={server_port},
                                                    chattutor_server='{chattutor_server}', token_id='{token_id}', use_as_default={use_as_default}""")
            cur.execute(f"""INSERT INTO lconfigstokens (user, course_id, course_url, run_locally, test_mode, is_static, built_with, server_port, chattutor_server, token_id, use_as_default)
                            VALUES ('{user}', '{course_id}', '{course_url}', {run_locally}, {test_mode}, {is_static}, '{build_with}', {server_port}, '{chattutor_server}', '{token_id}', {use_as_default}) 
                            ON DUPLICATE KEY UPDATE user='{user}', course_id='{course_id}', course_url='{course_url}',
                                                    run_locally={run_locally}, test_mode={test_mode}, is_static={is_static}, built_with='{build_with}', server_port={server_port},
                                                    chattutor_server='{chattutor_server}', token_id='{token_id}', use_as_default={use_as_default}""")
            con.commit()
            
    def get_config_by_course_id(self, course_id: str):
        with self.connect_to_messages_database() as con:
            cur = con.cursor()
            response = cur.execute(f"SELECT * FROM lconfigstokens WHERE course_id='{course_id}'")
            messages_arr = cur.fetchall()
            return messages_arr


    def get_default_config_for_url(self, url: str):
        with self.connect_to_messages_database() as con:
            cur = con.cursor()
            response = cur.execute(f"SELECT * FROM lconfigstokens WHERE course_url='{url}' AND use_as_default=1")
            messages_arr = cur.fetchall()
            return messages_arr

    def parse_messages(self, messages_arr):
        renderedString = (
            '<table class="messages-table"> <tr style="background-color: rgb(140, 0, 255); color: white"> '
            "<th> Role </th>"
            "<th> Content </th>"
            "<th> Number of clears </th>"
            "<th> Time </th>"
            "<th> Chat id </th>"
            " </tr>"
        )
        i = 0
        for message in messages_arr:
            role = message["role"]
            content = message["content"]
            chat_id = message["chat_key"]
            clear_number = message["clear_number"]
            time_cr = message["time_created"]
            style = "font-size: 10px; background-color: var(--msg-input-bg); overflow: hidden; padding: 2px; border-radius: 2px"
            side = "left"
            if role != "assistant":
                side = "right"

            chat_header = ""

            if i != 0:
                current_message = messages_arr[i]
                prev_message = messages_arr[i - 1]
                if current_message["chat_key"] != prev_message["chat_key"]:
                    chat_header = f"""
                        Chat id: {chat_id}
                    """

                if current_message["clear_number"] != prev_message["clear_number"]:
                    chat_header = f"""
                        Cleared {clear_number} from id {chat_id}
                    """
            else:
                chat_header = f"""
                    Chat id: {chat_id}
                """

            styl_td = ""
            i = i + 1

            timstp = int(time_cr)

            tr_header = ""
            if chat_header != "":
                tr_header = f'<tr style="color: var(--left-msg-txt); background-color: rgba(140, 0, 255, 0.5)"><td colspan="5">{chat_header}</td></tr>'

            msg_html = f"""
                            {tr_header}
                           <tr style="color: var(--left-msg-txt); {styl_td}">
                                <td style={styl_td}>{role}</td>
                                <td style={styl_td}>{content}</td>
                                <td style={styl_td}>{clear_number}</td>
                                <td style={styl_td}>{datetime.datetime.utcfromtimestamp(timstp / 1000)}</td>
                                <td style={styl_td}>{chat_id}</td>
                           </tr>
                       """
            renderedString += msg_html

        renderedString += "</table>"
        return renderedString
