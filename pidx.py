import os
import xml.etree.ElementTree as ET
from datetime import datetime
from xml.dom import minidom  # Import minidom for pretty printing

def generate_pidx_xml(root_dir):
    index_root = ET.Element('index')
    index_root.set('schemaVersion', '1.0.0')
    index_root.set('xs:noNamespaceSchemaLocation', 'PackIndex.xsd')
    index_root.set('xmlns:xs', 'http://www.w3.org/2001/XMLSchema-instance')
    
    vendor_element = ET.SubElement(index_root, 'vendor')
    vendor_element.text = 'NimaLTD'  # Replace with actual vendor
    
    url_element = ET.SubElement(index_root, 'url')
    url_element.text = 'https://github.com/nimaltd/STM32-PACK/raw/main/NimaLTD.pidx'  # Replace with actual URL
    
    timestamp_element = ET.SubElement(index_root, 'timestamp')
    timestamp_element.text = datetime.now().isoformat()
    
    pindex_element = ET.SubElement(index_root, 'pindex')
    
    # Walk through all directories and subdirectories
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            # Check for .pdsc files
            if filename.endswith('.pdsc'):
                pdsc_path = os.path.join(dirpath, filename)
                print(f"Processing {pdsc_path}")  # Debug print
                
                # Extract metadata from the .pdsc file
                try:
                    pdsc_metadata = extract_pdsc_metadata(pdsc_path)
                except Exception as e:
                    print(f"Error processing {pdsc_path}: {e}")
                    continue
                
                if pdsc_metadata:
                    # Create <pdsc> element
                    pdsc_element = ET.SubElement(pindex_element, 'pdsc')
                    pdsc_element.set('url', pdsc_metadata['url'])
                    pdsc_element.set('vendor', pdsc_metadata['vendor'])
                    pdsc_element.set('name', pdsc_metadata['name'])
                    pdsc_element.set('version', pdsc_metadata['version'])
                    
                    # Optional metadata
                    if 'description' in pdsc_metadata:
                        description_element = ET.SubElement(pdsc_element, 'description')
                        description_element.text = pdsc_metadata['description']
                    
                    if 'license' in pdsc_metadata:
                        license_element = ET.SubElement(pdsc_element, 'license')
                        license_element.text = pdsc_metadata['license']
                    
                    if 'keywords' in pdsc_metadata:
                        keywords_element = ET.SubElement(pdsc_element, 'keywords')
                        for keyword in pdsc_metadata['keywords']:
                            keyword_element = ET.SubElement(keywords_element, 'keyword')
                            keyword_element.text = keyword

    # Convert ElementTree to string and pretty print using minidom
    xml_str = ET.tostring(index_root, encoding='UTF-8')
    xml_str = minidom.parseString(xml_str).toprettyxml(indent="    ")
    
    # Write the XML to file in the current directory
    pidx_file = os.path.join(root_dir, 'NimaLTD.pidx')
    with open(pidx_file, 'w', encoding='UTF-8') as f:
        f.write(xml_str)
    
    print(f'.pidx file generated: {pidx_file}')

def extract_pdsc_metadata(pdsc_path):
    # Parse .pdsc file and extract metadata
    pdsc_metadata = {}

    try:
        tree = ET.parse(pdsc_path)
        root = tree.getroot()

        pdsc_metadata['vendor'] = root.find('vendor').text.strip()
        pdsc_metadata['name'] = root.find('name').text.strip()
        pdsc_metadata['url'] = root.find('url').text.strip()  # Assuming url is a direct child element
        pdsc_metadata['version'] = root.find('releases/release').get('version').strip()  # Assuming version is from the first release
        
        # Additional metadata
        description_element = root.find('description')
        if description_element is not None:
            pdsc_metadata['description'] = description_element.text.strip()
        
        license_element = root.find('license')
        if license_element is not None:
            pdsc_metadata['license'] = license_element.text.strip()
        
        keywords_element = root.find('keywords')
        if keywords_element is not None:
            pdsc_metadata['keywords'] = [keyword.text.strip() for keyword in keywords_element.findall('keyword')]

    except Exception as e:
        print(f"Error parsing {pdsc_path}: {e}")

    return pdsc_metadata

# Example usage:
if __name__ == '__main__':
    root_directory = os.getcwd()  # Use current directory as root
    generate_pidx_xml(root_directory)
