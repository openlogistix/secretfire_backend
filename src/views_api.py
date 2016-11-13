from flask import jsonify, request, json
from flask.views import MethodView
from collections import OrderedDict
import json

# Class APIViewSet creates a set of views for HTTP requests and routes them to a resource endpoint
class APIViewSet( MethodView ):
    
    # Constructor accepts options to determine the views to create
    def __init__( self, resource, table, connection, cursor ):

        # Store input parameter values into instance member variables
        self.resource   = resource
        self.connection = connection
        self.cursor     = cursor
        self.table      = table

        # Primary key is the first column of the table
        self.pri_key    = self.table.keys()[0]

    # Check if the columns to be changed exist in the table
    def check_database_inputs(change_dict, table):
        
        # Ensure that all columns in change_dict are in the table definition
        for col in change_dict.keys():
            if col not in table.keys():
                return 'Column %s not found in table!' % col
        
    # GET method will return the JSON for the resource with that ID
    def get(self, id):

        if id is None:
            return 'Not implemented yet!'
            # TODO return list of all resources

        else:
            try:
                self.cursor.execute('SELECT * FROM ' + self.resource + ' WHERE ' + \
                    self.pri_key + ' = %s', (str(id),) )
                record = self.cursor.fetchone()

                if not record:
                    return 'Unsuccessful. No resource with ' + self.pri_key + ' %d found.' % id, 404

                return jsonify( OrderedDict( zip( self.table.keys(), record ) ) )

            except Exception as e:
                return 'Unsuccessful. Error:\n' + str(e), 400

    # PUT method will update the record with the supplied JSON info
    def put(self, id):

        try:
            # Capture HTTP request data (JSON) and load into an update dictionary
            update_dict = OrderedDict( json.loads( request.data ) )

            # Ensure that if the id exists in update_dict, it matches the id provided in URL
            if self.pri_key in update_dict:
                if id != int( update_dict[self.pri_key] ):
                    return 'Error: ID does not match in body and URL', 400
            # If the id is not in update_dict, add it
            else:
                update_dict['id'] = id

            # Perform checks on dict describing values to be updated
            inputs_check = check_database_inputs( update_dict, self.table )
            if inputs_check:
                return 'Error: ' + inputs_check, 400

            # Execute and commit SQL command
            sql = 'UPDATE ' + self.resource + '\nSET\n' + ',\n'.join([x + ' = %(' + x + ')s' for x in update_dict.keys()]) + '\nWHERE ' + self.pri_key + ' = %(id)s;'
            self.cursor.execute( sql, update_dict )
            self.connection.commit()

            return 'Successfully updated resource with following SQL command:\n' + sql % update_dict, 201

        except Exception as e:
            return 'Unsuccessful. Error:\n' + str(e), 400

    # DELETE method will delete the record with the matching id
    def delete(self, id):

        # Execute and commit SQL command
        sql = 'DELETE FROM ' + self.resource + ' WHERE id = %s'
        self.cursor.execute(sql, {self.pri_key:id} )
        self.connection.commit()

        return 'Successfully deleted resource with ' + self.pri_key + ' %d' % id, 201

    # POST method will create a record with the supplied JSON info
    def post(self):

        try:
            # Capture HTTP request data in JSON
            insert_dict = OrderedDict( json.loads( request.data ) )

            # Perform checks on dict describing values to be inserted
            inputs_check = check_database_inputs( insert_dict, self.table )
            if inputs_check:
                return 'Error: ' + inputs_check

            # Execute and commit SQL command
            sql ='INSERT INTO ' + self.resource + '\n(' + ', '.join(insert_dict.keys()) + ')\nVALUES\n(' + \
                ', '.join( ['%(' + x + ')s' for x in insert_dict.keys()] )  + ');'
            self.cursor.execute( sql, insert_dict )
            self.connection.commit()

            return 'Successfully created resource with following SQL command:\n' + sql % insert_dict, 201

        except Exception as e:
            return 'Unsuccessful. Error:\n' + str(e)

# Create a custom API with standard HTTP methods for GET, POST, PUT, and DELETE
def create_API( server, resource_url, table, conn, curs ):
    
    resource = resource_url.split('/')[-2]
    assert len(resource) > 2, 'Resource URL should be in the form: /path/from/host/to/resource/'
    
    resource_views = APIViewSet.as_view( resource + '_api', resource, table, conn, curs )
    server.add_url_rule( resource_url, defaults={ 'id':None }, view_func=resource_views, methods=['GET'] )
    server.add_url_rule( resource_url, view_func=resource_views, methods=['POST'] )
    server.add_url_rule( resource_url + '<int:id>', view_func=resource_views, methods=['GET','PUT','DELETE'] )
