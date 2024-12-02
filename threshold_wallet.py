from sympy import mod_inverse
from random import SystemRandom
import sys
import colorama
from termcolor import colored

def shamir_secret_share(secret, n, t, prime):
    """
    Implement Shamir's Secret Sharing Scheme.
    
    This cryptographic technique splits a secret into n shares,
    such that any t shares can reconstruct the original secret.
    
    Args:
        secret (int): The secret to be shared
        n (int): Total number of shares to generate
        t (int): Threshold number of shares needed to reconstruct
        prime (int): Prime modulus for mathematical operations
    
    Returns:
        list: A list of (x, y) coordinate shares
    """
    if t > n:
        raise ValueError(colored("Threshold t cannot be greater than the number of shares n.", "red"))
    
    # Generate random coefficients for the polynomial
    # First coefficient is the secret, others are random
    coeffs = [secret] + [SystemRandom().randint(1, prime - 1) for _ in range(t - 1)]
    
    shares = []
    for i in range(1, n + 1):
        # Evaluate the polynomial at x = i using Horner's method
        # This creates a unique share for each participant
        y = sum([coeff * pow(i, exp, prime) for exp, coeff in enumerate(coeffs)]) % prime
        shares.append((i, y))
    
    return shares

def reconstruct_secret(shares, prime):
    """
    Reconstruct the secret using Lagrange interpolation.
    
    This method allows recovering the original secret 
    using any t shares out of the n total shares.
    
    Args:
        shares (list): Selected shares to reconstruct the secret
        prime (int): Prime modulus for mathematical operations
    
    Returns:
        int: The reconstructed secret
    """
    secret = 0
    for j, (xj, yj) in enumerate(shares):
        numerator, denominator = 1, 1
        for m, (xm, _) in enumerate(shares):
            if m != j:
                # Compute Lagrange basis polynomials
                numerator = (numerator * (-xm)) % prime
                denominator = (denominator * (xj - xm)) % prime
        
        # Compute Lagrange coefficient and interpolate
        lagrange_coeff = numerator * mod_inverse(denominator, prime) % prime
        secret = (secret + yj * lagrange_coeff) % prime
    
    return secret

def main():
    """
    Main function to demonstrate Threshold Secret Sharing.
    
    Walks through the process of:
    1. Generating secret shares
    2. Simulating share reconstruction
    3. Verifying secret recovery
    """
    # Initialize colorama for cross-platform colored output
    colorama.init()
    
    # Display introduction
    print(colored("🔐 Threshold Secret Sharing Demonstration 🔐", "magenta", attrs=['bold']))
    print(colored("A cryptographic method to securely distribute a secret", "cyan"))
    
    # Prime modulus (should be larger than the secret and number of shares)
    prime = 2089
    
    print("\n" + colored("🔢 Prime Modulus Details:", "yellow"))
    print(f"  Selected Prime: {prime}")
    print(f"  This ensures mathematical security of the secret sharing")
    
    # Get secret from user
    while True:
        try:
            secret = int(input("\n" + colored("Enter the secret (integer less than prime): ", "green")))
            if secret >= prime:
                print(colored("Error: Secret must be less than the prime modulus.", "red"))
                continue
            
            n = int(input(colored("Enter the total number of shares (n): ", "green")))
            t = int(input(colored("Enter the threshold (t): ", "green")))
            
            if t > n:
                print(colored("Error: Threshold t cannot be greater than the number of shares n.", "red"))
                continue
            
            break
        except ValueError:
            print(colored("Please enter valid integer values.", "red"))
    
    # Generate shares
    print("\n" + colored("🔀 Generating Secret Shares...", "blue"))
    shares = shamir_secret_share(secret, n, t, prime)
    
    print(colored("\n📜 Generated Shares:", "yellow"))
    for idx, share in enumerate(shares, 1):
        print(colored(f"Share {idx}: {share}", "cyan"))
    
    # Simulate share reconstruction
    print("\n" + colored("🤝 Reconstructing Secret...", "green"))
    print(colored(f"Need {t} out of {n} shares to reconstruct", "blue"))
    
    while True:
        try:
            # Prompt for share indices
            selected_indices_input = input(colored(f"\nEnter indices of {t} shares to reconstruct (e.g., 1,2,3): ", "green"))
            selected_indices = [int(i.strip()) for i in selected_indices_input.split(',')]
            
            # Validate selected shares
            if len(selected_indices) != t:
                print(colored(f"Error: Must select exactly {t} shares", "red"))
                continue
            
            selected_shares = [shares[i - 1] for i in selected_indices]
            
            # Reconstruct the secret
            reconstructed_secret = reconstruct_secret(selected_shares, prime)
            
            # Verify reconstruction
            print("\n" + colored("🔍 Verification:", "yellow"))
            print(colored(f"Original Secret:      {secret}", "blue"))
            print(colored(f"Reconstructed Secret: {reconstructed_secret}", "blue"))
            
            if reconstructed_secret == secret:
                print(colored("✅ Secret Successfully Reconstructed!", "green", attrs=['bold']))
            else:
                print(colored("❌ Failed to Reconstruct Secret Correctly", "red"))
            
            break
        except (ValueError, IndexError):
            print(colored("Invalid share selection. Please try again.", "red"))

if __name__ == "__main__":
    main()