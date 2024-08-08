# 1Password Service Account Configuration
## Introduction
This document provides the steps needed to configure a Vault in 1Password and to configure a Service Account to access that Vault for use with <b>Walman</b> and/or the [Walman Demo](https://github.com/twhalsema/walman/tree/main?tab=readme-ov-file#walman-demo).

## Configuration Steps

### SCREEN: Vaults
<b>PRESS:</b> New Vault  

![New Vault](/docimages/op_service_account/01_NewVault.png)

### SCREEN: Create a new vault
<b>ENTER:</b> Vault Name: walman_test  
    &emsp;<b>NOTE:</b> The name "walman_test" is required for the [Walman Demo](https://github.com/twhalsema/walman/tree/main?tab=readme-ov-file#walman-demo).  
<b>PRESS:</b> Create Vault  

![Create Vault](/docimages/op_service_account/02_VaultName.png)

### SCREEN: Vault Home
<b>PRESS:</b> Developer Tools  

![Developer Tools](/docimages/op_service_account/03_VaultHome.png)

### SCREEN: Developer Tools
<b>PRESS:</b> Service Account  

![Service Account](/docimages/op_service_account/04_DeveloperTools.png)

### SCREEN: Create a Service Account - Set up your service account
<b>ENTER:</b> Service account name: walman_test  
      &emsp;<b>NOTE:</b> The name `walman_test` is required for the [Walman Demo](https://github.com/twhalsema/walman/tree/main?tab=readme-ov-file#walman-demo).   
<b>PRESS:</b> Next  

![Create Service Account](/docimages/op_service_account/05_CreateServiceAccount.png)

### SCREEN: Create a Service Account - Grant vault access
<b>CHECK:</b> walman_test (or whatever you named your vault)  
<b>PRESS:</b> The gear symbol  
    &emsp;<b>CHECK:</b> Read Items  
    &emsp;<b>CHECK:</b> Write Items  
<b>PRESS:</b> Create Account  

![Grant Vault Access](/docimages/op_service_account/06_GrantVaultAccess.png)

### SCREEN: Create a Service Account - Save service account token
<b>PRESS:</b> The <b>copy</b> button.  
    &emsp;<b>NOTE:</b> Copy this value to notepad. You will be prompted for this when running `main.yaml` if using the [Walman Demo](https://github.com/twhalsema/walman/tree/main?tab=readme-ov-file#walman-demo). You will need to use it in `op login` if installing `walman.py` manually.  
<b>PRESS:</b> Save in 1Password  
    &emsp;<b>NOTE:</b> Store this value in 1Password since you can't retrieve it again. If you lose it, you'll need to rotate the token to get a new one.  

![Copy Service Account Token](/docimages/op_service_account/07_ServiceAccountToken.png)

### SCREEN: Save in 1Password
<b>SELECT:</b> Whichever vault in which you want to store the service account's token.  
<b>PRESS:</b> Save  

![Save Service Account Token](/docimages/op_service_account/08_SaveToken.png)

### SCREEN: Create a Service Account - Save service account token (2)
<b>PRESS:</b> View Details  

![View Details](/docimages/op_service_account/09_ViewDetails.png)

