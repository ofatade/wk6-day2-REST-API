from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from connection import connection, Error

app = Flask(__name__)
ma = Marshmallow(app)

#Create the Customer table schema, to define the structure of our data
class MemberSchema(ma.Schema):
    id = fields.Int(dump_only= True) # dump_only means we don't have to input data for this field
    member_name = fields.String(required= True) # To be valid, this needs a value
    email = fields.String()
    phone = fields.String()

    class Meta:
        fields = ("member_name", "email", "phone")

member_schema = MemberSchema()
members_schema = MemberSchema(many= True)


@app.route('/') # default landing page
def home():
    return "Hello, Flask!"

@app.route('/darezy') # blahblah.com/cool
def darezy():
    return "My name is Dare Fatade aka Darezy!!!!!! extravaganzaaaaaaaaaaaaaaaaa!!"

# Reads all customer data via a GET request
@app.route("/member", methods = ['GET'])
def get_member():
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor(dictionary= True) # returns us a dictionary of table data instead of a tuple, our schema meta class with cross check the contents of the dictionaries that are returned

            # Write our query to GET all users
            query = "SELECT * FROM members;"

            cursor.execute(query)

            member = cursor.fetchall()

        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
                return members_schema.jsonify(member)
            

# Create a new customer with a POST request
@app.route("/member", methods= ["POST"])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.message), 400
    
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            # New customer data
            new_member = (member_data["member_name"], member_data["email"], member_data["phone"])

            # query
            query = "INSERT INTO members (member_name, email, phone) VALUES (%s, %s, %s)"

            # Execute the query with new_customer data
            cursor.execute(query, new_member)
            conn.commit()

            return jsonify({'message': 'New member added successfully!'}), 200
        
        except Error as e:
            return jsonify(e.messages), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Databse connection failed"}), 500

@app.route("/member/<int:id>", methods= ["PUT"]) # dynamic route that will change based off of different query parameters
def update_member(id):
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            check_query = "SELECT * FROM members WHERE id = %s"
            cursor.execute(check_query, (id,))
            member = cursor.fetchone()
            if not member:
                return jsonify({"error": "member was not found."}), 404
            
            # unpack customer info
            updated_member = (member_data['member_name'], member_data['email'], member_data['phone'], id)

            query = "UPDATE member SET member_name = %s, email = %s, phone = %s WHERE id = %s"

            cursor.execute(query, updated_member)
            conn.commit()

            return jsonify({'message': f"Successfully update user {id}"}), 200
        except Error as e:
            return jsonify(e.messages), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Databse connection failed"}), 500


@app.route("/member/<int:id>", methods=['DELETE'])
def delete_member(id):
    
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            check_query = "SELECT * FROM members WHERE id = %s"
            cursor.execute(check_query, (id,))
            member = cursor.fetchone()
            if not member:
                return jsonify({"error": "Member not found"})
            
            query = "DELETE FROM members WHERE id = %s"
            cursor.execute(query, (id,))
            conn.commit()

            return jsonify({"message": f"member {id} was successfully destroyed!"})
        except Error as e:
            return jsonify(e.messages), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Databse connection failed"}), 500
    
    
if __name__ == "__main__":
     app.run(debug=True)