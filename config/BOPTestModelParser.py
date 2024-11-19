import json
from pathlib import Path
import re

class BOPTestModelParser:
    def __init__(self, testcase_path):
        self.testcase_path = Path(testcase_path)
        self.modelica_path = self.testcase_path / "models"
        self.config_path = self.testcase_path / "config.json"
        
    def parse_modelica_parameters(self):
        """Parse Modelica (.mo) files for parameters"""
        parameters = {}
        
        # Main model file should be in models directory
        model_files = list(self.modelica_path.glob("*.mo"))
        
        for file_path in model_files:
            with open(file_path, 'r') as f:
                content = f.read()
                
                # Look for parameter declarations
                parameter_matches = re.finditer(
                    r'parameter\s+(\w+)\s+(\w+)\s*=\s*([^;]+);(?:\s*\/\/\s*(.*))?',
                    content
                )
                
                for match in parameter_matches:
                    param_type, param_name, param_value, comment = match.groups()
                    parameters[param_name] = {
                        'type': param_type,
                        'value': param_value.strip(),
                        'description': comment.strip() if comment else ''
                    }
                    
                # Look for building envelope properties
                envelope_matches = re.finditer(
                    r'Buildings\.(\w+)\.(\w+)\s*\((.*?)\)',
                    content
                )
                
                for match in envelope_matches:
                    component, type_name, properties = match.groups()
                    parameters[f"{component}_{type_name}"] = self._parse_properties(properties)
                    
        return parameters
    
    def parse_config_file(self):
        """Parse testcase config.json file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found at {self.config_path}")
            
        with open(self.config_path, 'r') as f:
            config = json.load(f)
            
        return config
    
    def _parse_properties(self, properties_str):
        """Parse property assignments in Modelica syntax"""
        properties = {}
        
        # Split by comma, handling nested parentheses
        props = re.findall(r'(\w+)\s*=\s*([^,]+)(?:,|$)', properties_str)
        
        for name, value in props:
            properties[name] = value.strip()
            
        return properties
    
    def extract_thermal_properties(self):
        """Extract specific thermal properties"""
        thermal_props = {
            'envelope': {},
            'zones': {},
            'hvac': {}
        }
        
        modelica_params = self.parse_modelica_parameters()
        config = self.parse_config_file()
        
        # Extract envelope properties
        envelope_patterns = {
            'wall_construction': r'wall\w*Construction',
            'window_construction': r'window\w*Construction',
            'floor_construction': r'floor\w*Construction',
            'roof_construction': r'roof\w*Construction'
        }
        
        for component, pattern in envelope_patterns.items():
            matches = {k: v for k, v in modelica_params.items() 
                      if re.match(pattern, k, re.IGNORECASE)}
            if matches:
                thermal_props['envelope'][component] = matches
        
        # Extract zone properties
        zone_patterns = {
            'volume': r'V\w*',
            'floor_area': r'A\w*floor',
            'height': r'h\w*room'
        }
        
        for property_name, pattern in zone_patterns.items():
            matches = {k: v for k, v in modelica_params.items() 
                      if re.match(pattern, k, re.IGNORECASE)}
            if matches:
                thermal_props['zones'][property_name] = matches
        
        return thermal_props

def main():
    # Example usage
    parser = BOPTestModelParser("path/to/multizone_office_simple_air")
    thermal_properties = parser.extract_thermal_properties()
    
    # Print extracted properties in a structured way
    print("Extracted Thermal Properties:")
    print("\nEnvelope Properties:")
    for component, props in thermal_properties['envelope'].items():
        print(f"\n{component}:")
        for name, value in props.items():
            print(f"  {name}: {value}")
    
    print("\nZone Properties:")
    for property_name, values in thermal_properties['zones'].items():
        print(f"\n{property_name}:")
        for zone, value in values.items():
            print(f"  {zone}: {value}")
            
    # Convert to simulation parameters
    simulation_params = convert_to_simulation_parameters(thermal_properties)
    return simulation_params

def convert_to_simulation_parameters(thermal_properties):
    """Convert extracted properties to simulation parameters"""
    return {
        'building': {
            'zones': {
                zone: {
                    'volume': float(props['value']) 
                    for zone, props in thermal_properties['zones']['volume'].items()
                },
                'floor_area': {
                    zone: float(props['value'])
                    for zone, props in thermal_properties['zones']['floor_area'].items()
                },
                'height': {
                    zone: float(props['value'])
                    for zone, props in thermal_properties['zones']['height'].items()
                }
            },
            'envelope': {
                'walls': {
                    'u_value': extract_u_value(
                        thermal_properties['envelope']['wall_construction']
                    ),
                    'thermal_mass': extract_thermal_mass(
                        thermal_properties['envelope']['wall_construction']
                    )
                },
                'windows': {
                    'u_value': extract_u_value(
                        thermal_properties['envelope']['window_construction']
                    ),
                    'g_value': extract_g_value(
                        thermal_properties['envelope']['window_construction']
                    )
                }
            }
        }
    }

def extract_u_value(construction_props):
    """Extract U-value from construction properties"""
    # Implementation depends on specific Modelica model structure
    pass

def extract_thermal_mass(construction_props):
    """Extract thermal mass from construction properties"""
    # Implementation depends on specific Modelica model structure
    pass

def extract_g_value(window_props):
    """Extract solar heat gain coefficient from window properties"""
    # Implementation depends on specific Modelica model structure
    pass

if __name__ == "__main__":
    params = main()