import random
import time
import hashlib
import mysql.connector
from mysql.connector import Error
import base64
from cryptography.fernet import Fernet

fernetKey = 'nNjpIl9Ax2LRtm-p6ryCRZ8lRsL0DtuY0f9JeAe2wG0='
fernetKey = base64.urlsafe_b64encode(fernetKey.encode())



connection = mysql.connector.connect(host='', database='', user='', password='')



class SSO:

    @staticmethod
    def initTable():
        connection = None
        cursor = None
        try:
            cursor = connection.cursor()

            # Drop the table if it exists
            cursor.execute('DROP TABLE IF EXISTS sso_tokens;')
            connection.commit()
            
            cursor.execute('DROP TABLE IF EXISTS config;')
            connection.commit()

            create_table_query = '''
            CREATE TABLE IF NOT EXISTS sso_tokens (
                id INT AUTO_INCREMENT,     
                token VARCHAR(1024),
                PRIMARY KEY (id)
            )
            '''

            create_config_table_query = '''
            CREATE TABLE IF NOT EXISTS config (
                id INT AUTO_INCREMENT,
                guildid VARCHAR(1024),
                helloMessage VARCHAR(1024),
                PRIMARY KEY (id)
            )
            '''

            cursor.execute(create_table_query)
            connection.commit()
            print("Table 'sso_tokens' created successfully.")
            
            cursor.execute(create_config_table_query)
            connection.commit()
            print("Table 'config' created successfully.")

        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            if connection:
                connection.rollback()

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
                print("MySQL connection is closed.")
        
        return "Table 'sso_tokens' created successfully. Table 'config' created successfully."
    
    @staticmethod
    def genSSOToken(guildID, authorID):
        print('Generating SSO token...')
        current_time = int(time.time())
        random_number = random.randint(1, 1000)
        expiry_time = current_time + 900 # 15 mins which should be enough timer for the user to use the panel 

        cipher_suite = Fernet(base64.urlsafe_b64decode(fernetKey))
        encrypted_expiry_time = cipher_suite.encrypt(str(expiry_time).encode())
        encrypted_guildID = cipher_suite.encrypt(str(guildID).encode())
        encrypted_authorID = cipher_suite.encrypt(str(authorID).encode())
        sso_token = hashlib.sha256((str(current_time) + str(random_number) + str(guildID) + str(authorID)).encode()).hexdigest()
        sso_token = sso_token + '+' + str(encrypted_expiry_time.decode()) + '+' + str(encrypted_guildID.decode()) + '+' + str(encrypted_authorID.decode())

        cursor = connection.cursor()

        
        insert_query = "INSERT INTO sso_tokens (token) VALUES (%s)"
        cursor.execute(insert_query, (sso_token,))

        
        connection.commit()

        cursor.close()
        connection.close()
        
        return sso_token

    @staticmethod
    def checkSSOToken(ssoToken):
        if ssoToken is None:
            return False, 0

        cursor = connection.cursor()

        query = "SELECT * FROM sso_tokens WHERE token = %s"
        cursor.execute(query, (ssoToken,))
        result = cursor.fetchall()

        if not result:
            return False, 0
        else:
            token_parts = result[0][1].split('+')
            if len(token_parts) < 4:
                return False, 0

            cipher_suite = Fernet(base64.urlsafe_b64decode(fernetKey))

            try:
                decrypted_expiry_time = cipher_suite.decrypt(token_parts[1].encode()).decode()
                expiry_time = int(decrypted_expiry_time)
            except (ValueError, IndexError):
                return False, 

            current_time = int(time.time())
            time_remaining = expiry_time - current_time

            try:
                guildid = cipher_suite.decrypt(token_parts[2].encode()).decode()
                authorid = cipher_suite.decrypt(token_parts[3].encode()).decode()
            except IndexError:
                return False, 0

            if time_remaining > 0:
                return True, time_remaining, guildid, authorid
            else:
                return False, -1, guildid, authorid
            
    @staticmethod
    def getRecentToken(guildID, authorID):
        connection = None
        cursor = None
        try:
            cursor = connection.cursor()

            query = "SELECT token FROM sso_tokens ORDER BY id DESC"
            cursor.execute(query)
            tokens = cursor.fetchall()

            cipher_suite = Fernet(base64.urlsafe_b64decode(fernetKey))
            current_time = int(time.time())

            for token_row in tokens:
                token = token_row[0]
                token_parts = token.split('+')
                if len(token_parts) < 4:
                    continue

                try:
                    decrypted_expiry_time = cipher_suite.decrypt(token_parts[1].encode()).decode()
                    decrypted_guildID = cipher_suite.decrypt(token_parts[2].encode()).decode()
                    decrypted_authorID = cipher_suite.decrypt(token_parts[3].encode()).decode()

                    expiry_time = int(decrypted_expiry_time)

                    if decrypted_guildID == str(guildID) and decrypted_authorID == str(authorID) and expiry_time > current_time:
                        return token
                except:
                    continue

            return "No valid token found for the specified guildID and authorID."

        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            return "Failed to connect to the database."

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    @staticmethod
    async def initGuildTable(guildID):
        connection = None
        cursor = None
        try:
            cursor = connection.cursor()
            
            insert_query = "INSERT INTO config (guildid) VALUES (%s)"
            cursor.execute(insert_query, (guildID,))
            connection.commit()
            
            # Put the default values in the table
            insert_query = "INSERT INTO config (guildid, helloMessage) VALUES (%s, %s)"
            cursor.execute(insert_query, (guildID, 'Hello there!'))
            
            return True
        
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            return False
        
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
                