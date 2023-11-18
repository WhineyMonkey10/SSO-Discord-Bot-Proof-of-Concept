import random
import time
import hashlib
import mysql.connector
from mysql.connector import Error
import base64
from cryptography.fernet import Fernet

fernetKey = 'nNjpIl9Ax2LRtm-p6ryCRZ8lRsL0DtuY0f9JeAe2wG0='
fernetKey = base64.urlsafe_b64encode(fernetKey.encode())


class SSO:

    @staticmethod
    def initTable():
        connection = None
        cursor = None
        try:
            connection = mysql.connector.connect(host='...', database='...', user='...', password='...')
            cursor = connection.cursor()

            # Drop the table if it exists
            cursor.execute('DROP TABLE IF EXISTS sso_tokens;')
            connection.commit()

            # Create the table
            create_table_query = '''
CREATE TABLE IF NOT EXISTS sso_tokens (
    id INT AUTO_INCREMENT,     
    token VARCHAR(1024),
    token_hash VARBINARY(32),
    PRIMARY KEY (id)
)
            '''
            cursor.execute(create_table_query)
            connection.commit()
            print("Table 'sso_tokens' created successfully.")

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
        
        return "Table 'sso_tokens' created successfully."
    
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

        connection = mysql.connector.connect(host='88.198.2.92', database='s646_SSO_Testing', user='u646_xGpPpLpaOU', password='.tTmdBNcOh5Vl.Vh!bnBYjKx')
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

        connection = mysql.connector.connect(host='88.198.2.92', database='s646_SSO_Testing', user='u646_xGpPpLpaOU', password='.tTmdBNcOh5Vl.Vh!bnBYjKx')
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