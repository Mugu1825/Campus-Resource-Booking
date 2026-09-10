from bson import ObjectId

def serialize_doc(doc):
    if not doc:
        return doc
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        new_doc = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                new_doc[key] = str(value)
            elif isinstance(value, (dict, list)):
                new_doc[key] = serialize_doc(value)
            else:
                new_doc[key] = value
                
        # Aliases for frontend compatibility
        if '_id' in new_doc:
            new_doc['id'] = str(new_doc['_id'])
        if 'account_status' in new_doc and 'status' not in new_doc:
            new_doc['status'] = new_doc['account_status']
        if 'register_no' in new_doc and 'reg_no' not in new_doc:
            new_doc['reg_no'] = new_doc['register_no']
        if 'date_start' in new_doc and 'start_date' not in new_doc:
            new_doc['start_date'] = new_doc['date_start']
        if 'date_end' in new_doc and 'end_date' not in new_doc:
            new_doc['end_date'] = new_doc['date_end']
            
        return new_doc
    if isinstance(doc, ObjectId):
        return str(doc)
    return doc
