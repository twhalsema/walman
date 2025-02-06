# 1Password Service Account Configuration
## Introduction
This document provides the steps needed to configure a Vault in 1Password and to configure a Service Account to access that Vault for use with **Walman** and/or the [Walman Demo](https://github.com/twhalsema/walman/tree/main?tab=readme-ov-file#walman-demo).

## Configuration Steps

### SCREEN: Vaults
**PRESS:** New Vault  

![New Vault](/docimages/op_service_account/01_NewVault.png)

### SCREEN: Create a new vault
**ENTER:** Vault Name: walman_test  
    &emsp;**NOTE:** The name "walman_test" is required for the [Walman Demo](https://github.com/twhalsema/walman/tree/main?tab=readme-ov-file#walman-demo).  
**PRESS:** Create Vault  

![Create Vault](/docimages/op_service_account/02_VaultName.png)

### SCREEN: Vault Home
**PRESS:** Developer Tools  

![Developer Tools](/docimages/op_service_account/03_VaultHome.png)

### SCREEN: Developer Tools
**PRESS:** Service Account  

![Service Account](/docimages/op_service_account/04_DeveloperTools.png)

### SCREEN: Create a Service Account - Set up your service account
**ENTER:** Service account name: walman_test  
      &emsp;**NOTE:** The name `walman_test` is required for the [Walman Demo](https://github.com/twhalsema/walman/tree/main?tab=readme-ov-file#walman-demo).   
**PRESS:** Next  

![Create Service Account](/docimages/op_service_account/05_CreateServiceAccount.png)

### SCREEN: Create a Service Account - Grant vault access
**CHECK:** walman_test (or whatever you named your vault)  
**PRESS:** The gear symbol  
    &emsp;**CHECK:** Read Items  
    &emsp;**CHECK:** Write Items  
**PRESS:** Create Account  

![Grant Vault Access](/docimages/op_service_account/06_GrantVaultAccess.png)

### SCREEN: Create a Service Account - Save service account token
**PRESS:** The **copy** button.  
    &emsp;**NOTE:** Copy this value to notepad. You will be prompted for this when running `ansible-playbook main.yaml` if using the [Walman Demo](https://github.com/twhalsema/walman/tree/main?tab=readme-ov-file#walman-demo). You will need to use it when configuring 1Password CLI if installing `walman.py` manually.
**PRESS:** Save in 1Password  
    &emsp;**NOTE:** Store this value in 1Password since you can't retrieve it again. If you lose it, you'll need to rotate the token to get a new one.  

![Copy Service Account Token](/docimages/op_service_account/07_ServiceAccountToken.png)

### SCREEN: Save in 1Password
**SELECT:** Whichever vault in which you want to store the service account's token.  
**PRESS:** Save  

![Save Service Account Token](/docimages/op_service_account/08_SaveToken.png)

### SCREEN: Create a Service Account - Save service account token (2)
**PRESS:** View Details  

![View Details](/docimages/op_service_account/09_ViewDetails.png)
