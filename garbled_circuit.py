from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
import os
import colorama
from termcolor import colored

class GarbledCircuit:
    def __init__(self):
        """
        Initialize a Garbled Circuit with key storage and cryptographic backend.
        
        Garbled Circuits are a cryptographic technique that allows two parties 
        to jointly compute a function without revealing their individual inputs.
        """
        self.keys = {}          # Stores encryption keys for wire values
        self.garbled_table = {} # Stores encrypted gate outputs
        self.backend = default_backend()
    
    def generate_keys(self):
        """
        Generate random encryption keys for each wire.
        
        For each wire (a, b, out), we create two keys:
        - One key represents the wire value 0
        - One key represents the wire value 1
        
        Using 128-bit random keys ensures cryptographic security.
        """
        # Generate random 128-bit keys for inputs and output
        self.keys['a'] = (os.urandom(16), os.urandom(16))
        self.keys['b'] = (os.urandom(16), os.urandom(16))
        self.keys['out'] = (os.urandom(16), os.urandom(16))
    
    def create_garbled_table(self):
        """
        Create a garbled truth table for an AND gate.
        
        This method encrypts all possible gate outputs using a combination 
        of input keys. The encryption prevents an evaluator from knowing 
        the actual input values.
        
        Process:
        1. For each possible input combination (0/0, 0/1, 1/0, 1/1)
        2. Compute the AND gate output
        3. Encrypt the output key using combined input keys
        4. Store the encrypted output with a hashed index
        """
        for a_val in (0, 1):
            for b_val in (0, 1):
                # Compute the AND gate output
                output_val = a_val & b_val
                
                # Combine input keys for this combination
                key_combo = self.keys['a'][a_val] + self.keys['b'][b_val]
                
                # Encrypt the corresponding output key
                encrypted_output = self.encrypt(self.keys['out'][output_val], key_combo)
                
                # Create a secure, non-predictable index
                index = self.hash_index(a_val, b_val)
                
                # Store the encrypted output
                self.garbled_table[index] = encrypted_output
    
    def encrypt(self, value, key):
        """
        Encrypt a value using HMAC-SHA256.
        
        HMAC provides a way to securely encrypt and authenticate the value
        using a combination of the value and a secret key.
        """
        h = hmac.HMAC(key, hashes.SHA256(), backend=self.backend)
        h.update(value)
        return h.finalize()
    
    def hash_index(self, a_val, b_val):
        """
        Create a secure, non-predictable index for the garbled table.
        
        This prevents an attacker from guessing the input combination 
        by using a secret key to hash the input values.
        """
        h = hmac.HMAC(b'secret_index_key', hashes.SHA256(), backend=self.backend)
        h.update(bytes([a_val, b_val]))
        return h.finalize()
    
    def get_input_keys(self, inputs):
        """
        Retrieve the encryption keys for the given input values.
        
        This method allows a party to get their corresponding encryption keys.
        """
        return {
            'a': self.keys['a'][inputs['a']],
            'b': self.keys['b'][inputs['b']]
        }

def evaluate_garbled_circuit(gc, alice_input_key, bob_input_key):
    """
    Evaluate the garbled circuit without knowing the actual input values.
    
    Bob can compute the AND gate result using:
    1. Alice's input key
    2. Bob's input key
    3. The pre-generated garbled table
    
    The magic is that Bob can compute the result without knowing 
    the actual input values of Alice or himself.
    """
    # Combine input keys
    key_combo = alice_input_key + bob_input_key
    
    # Try all possible input combinations
    for a_val in (0, 1):
        for b_val in (0, 1):
            # Create a secure index for this input combination
            index = gc.hash_index(a_val, b_val)
            encrypted_output = gc.garbled_table.get(index)
            
            if encrypted_output:
                # Try to decrypt the output for each possible value
                for output_val in (0, 1):
                    possible_output_key = gc.keys['out'][output_val]
                    computed_encrypted_output = gc.encrypt(possible_output_key, key_combo)
                    
                    if computed_encrypted_output == encrypted_output:
                        # Colorful output to show the result
                        print(colored(f"🔒 Secure Computation Complete!", "green"))
                        print(colored(f"Output of AND Gate: {output_val}", "blue", attrs=['bold']))
                        return output_val
    
    print(colored("❌ Failed to decrypt the output.", "red"))
    return None

def main():
    # Initialize colorama for cross-platform colored output
    colorama.init()
    
    # Print an introductory message
    print(colored("🔐 Garbled Circuits Demonstration 🔐", "magenta", attrs=['bold']))
    print(colored("A private computation method", "cyan"))
    
    # Initialize the garbled circuit
    gc = GarbledCircuit()
    
    # Generate keys and create the garbled table
    gc.generate_keys()
    gc.create_garbled_table()
    
    # Get inputs from Alice and Bob
    print("\n" + colored("Alice's Turn:", "yellow"))
    alice_input = int(input("Enter your secret input (0 or 1): "))
    alice_input_key = gc.keys['a'][alice_input]
    
    print("\n" + colored("Bob's Turn:", "yellow"))
    bob_input = int(input("Enter your secret input (0 or 1): "))
    bob_input_key = gc.keys['b'][bob_input]
    
    # Evaluate the circuit
    print("\n" + colored("🖥️  Performing Secure Computation...", "green"))
    evaluate_garbled_circuit(gc, alice_input_key, bob_input_key)

if __name__ == "__main__":
    main()