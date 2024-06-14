from flask import Flask, request, jsonify
from mysql.connector.errors import IntegrityError
import mysql.connector
from passlib.hash import sha256_crypt
from flask_cors import CORS
from flask_marshmallow import Marshmallow

app = Flask(__name__)
CORS(app)

dbConnection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='akAS#.22ml',
    database='rentify_schema'
)
cursor = dbConnection.cursor(dictionary=True)
ma = Marshmallow(app)

class PropertiesSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'location', 'area', 'bedrooms', 'bathrooms', 'price', 'near_by', 'seller_id')

properties_schema = PropertiesSchema()
properties_schema = PropertiesSchema(many=True)


# ===== User Registration
@app.route('/api/register', methods = ['POST'])
def register():
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    email = request.json['email']
    phone_number = request.json['phone_number']
    password = sha256_crypt.hash(str(request.json['password']))
    user_type = request.json['user_type']
    try:
        cursor.execute("INSERT INTO users (first_name, last_name, email, phone_number, password, user_type) VALUES (%s, %s, %s, %s, %s, %s)",
                (first_name, last_name, email, phone_number, password, user_type))
        dbConnection.commit()
        return jsonify({"status": "registered"}), 201
    except IntegrityError as e:
            if e.errno == 1062:
                return jsonify({"status": "register error Email already exists"}), 208
            else:
                return jsonify({"status": "register error"}), 401
# ====== User Login
@app.route('/api/login', methods = ['POST'])
def login():
    email = request.json['email']
    check_password = request.json['password']
    user_type = request.json['user_type']
    # try:
    cursor.execute("SELECT password, email, user_type FROM users WHERE email = %s", (email,))
    userData = cursor.fetchone()
    # print(userData['user_type'])
    if userData:
        if sha256_crypt.verify(check_password, userData['password']) and (user_type == userData['user_type']):
            
            if user_type == 1:
                res = {"user_type": "buyer"}
                return jsonify(res), 200
            else:
                res = {"user_type": "seller"}
                return jsonify(res), 200
        else:
            return jsonify({"status": "Invalid Credentials!"}), 401
    else:
            return jsonify({"status": "Invalid Credentials!"}), 401
    # except TypeError:
    #         return jsonify({"status": "Invalid Credentials!"})



# ====== Add Property (Seller Action)
@app.route('/api/properties', methods = ['POST'])
def addProperty():
    title = request.json['title']
    description = request.json['description']
    location = request.json['location']
    area = request.json['area']
    bedrooms = request.json['bedrooms']
    bathrooms = request.json['bathrooms']
    price = request.json['price']
    near_by = request.json['near_by']
    seller_id = request.json['seller_id']

    cursor.execute("INSERT INTO properties (title, description, location, area, bedrooms, bathrooms, price, near_by, seller_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (title, description, location, area, bedrooms, bathrooms, price, near_by, seller_id))
    # propertyDetails = cursor.fetchone()
    dbConnection.commit()
    # for propertyDetail in propertyDetails:
    #     print(propertyDetail)
    # print(jsonify(propertyDetails))
    # print(properties_schema.jsonify(propertyDetails))
    return jsonify({'status': 'property posted'}), 201


# ====== Get All Properties (Seller)
@app.route('/api/sellers/<string:id>/properties', methods = ['GET'])
def getSellerProperty(id):
    cursor.execute("SELECT * FROM properties WHERE seller_id = %s", (id,))
    propertyDetails = cursor.fetchall()
    if propertyDetails is None:
        return jsonify({"status" : "Property not uploaded"}), 404
    else:
        return jsonify(propertyDetails), 201


# ====== Update Property (Seller Action)
@app.route('/api/properties/<string:id>', methods = ['GET'])
def getUpdateProperty(id):
    cursor.execute('SELECT * FROM properties WHERE id = %s', (id,))
    propertyDetails = cursor.fetchone()
    return jsonify(propertyDetails), 200



@app.route('/api/properties/<string:id>', methods = ['PUT'])
def updateProperty(id):
    cursor.execute('SELECT * FROM properties WHERE id = %s', (id,))
    propertyDetails = cursor.fetchone()

    title = request.json['title']
    description = request.json['description']
    location = request.json['location']
    area = request.json['area']
    bedrooms = request.json['bedrooms']
    bathrooms = request.json['bathrooms']
    price = request.json['price']
    near_by = request.json['near_by']

    cursor.execute("UPDATE properties SET title = %s, description = %s, location = %s, area = %s, bedrooms = %s, bathrooms = %s, price = %s, near_by = %s WHERE id = %s",
               (title, description, location, area, bedrooms, bathrooms, price, near_by, id))
    updatedDetails = cursor.fetchone()
    dbConnection.commit()
    return jsonify({'status': 'Updated'}), 200


# ====== Delete Property (Seller Action)
@app.route('/api/properties/<string:id>', methods = ['DELETE'])
def deleteProperty(id):
    cursor.execute('DELETE FROM properties WHERE id = %s', (id,))
    dbConnection.commit()
    return jsonify({'status': 'deleted'}), 200


# ====== Get All Properties (Buyer Flow)
@app.route('/api/properties', methods = ['GET'])
def getAllProperty():
    cursor.execute("SELECT * FROM properties")
    propertiesDetails = cursor.fetchall()
    if propertiesDetails is None:
        return jsonify({"status" : "Properties not there"}), 404
    else:
        return jsonify(propertiesDetails), 200






# ====== Mark Property as Interested (Buyer Action)
@app.route('/api/properties/<string:id>/interested', methods = ['POST'])
def interestedAction():
    pass


# ====== Add Like to Property (Buyer Action)
@app.route('/api/properties/<string:id>/like', methods = ['POST'])
def likeAction():
    pass
# ====== Get Seller Details
# @app.route('/api/sellers/<string:id>/details', methods = ['GET'])
# def updateProperty():
#     pass

# ======================log out====================
# @app.route("/logout", methods=['GET'])
# def logout():
#     session.clear()
#     return redirect(url_for('index'))


if __name__ == '__main__':
    app.secret_key = 'flask_api'
    app.run(debug=True)
