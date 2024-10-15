import boto3
from collections import defaultdict
from openpyxl import Workbook, load_workbook
from io import BytesIO

def get_kv_map(image):
    """
    Analyze the document using AWS Textract to get key-value pairs.
    """
    client = boto3.client('textract')
    
    # Read the image bytes
    image_bytes = image.read()
    
    # Analyze the document using Textract
    response = client.analyze_document(
        Document={'Bytes': image_bytes}, 
        FeatureTypes=['FORMS']
    )

    # Get the text blocks
    blocks = response['Blocks']

    # Initialize key, value, and block maps
    key_map = {}
    value_map = {}
    block_map = {}
    
    for block in blocks:
        block_id = block['Id']
        block_map[block_id] = block
        if block['BlockType'] == "KEY_VALUE_SET":
            if 'KEY' in block['EntityTypes']:
                key_map[block_id] = block
            else:
                value_map[block_id] = block

    return key_map, value_map, block_map

def get_kv_relationship(key_map, value_map, block_map):
    """
    Map the key-value relationships from the blocks.
    """
    kvs = defaultdict(list)
    for block_id, key_block in key_map.items():
        value_block = find_value_block(key_block, value_map)
        key = get_text(key_block, block_map)
        val = get_text(value_block, block_map)
        kvs[key].append(val)
    return kvs

def find_value_block(key_block, value_map):
    """
    Find the value block associated with the key block.
    """
    for relationship in key_block['Relationships']:
        if relationship['Type'] == 'VALUE':
            for value_id in relationship['Ids']:
                value_block = value_map[value_id]
    return value_block

def get_text(result, blocks_map):
    """
    Extract text from a block of text.
    """
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] == 'SELECTED':
                            text += 'X'
    return text.strip()

def write_kvs_to_excel(kvs, ws):
    """
    Write key-value pairs into the existing worksheet.
    """
    for key, values in kvs.items():
        for value in values:
            ws.append([key, value])

def process_images(images):
    """
    Process multiple images and create a single Excel file.
    """
    # Create a new workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Key-Value Pairs"

    # Add headers
    ws.append(["Key", "Value"])

    # Process each image
    for image in images:
        key_map, value_map, block_map = get_kv_map(image)
        kvs = get_kv_relationship(key_map, value_map, block_map)
        write_kvs_to_excel(kvs, ws)

    # Save the workbook to a BytesIO object
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return output

def main(images):
    output_file = process_images(images)
    return output_file
