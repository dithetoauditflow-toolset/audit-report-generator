# UIF Report Generator - Copy-Paste Text Configuration

This directory contains the configuration file for all copy-paste ready text used in the UIF Report Generator application.

## File Structure

- `copy_paste_text.py` - Main configuration file containing all text templates
- `README.md` - This documentation file

## How to Edit Copy-Paste Text

### 1. Open the Configuration File

Open `config/copy_paste_text.py` in any text editor. The file is organized into logical sections:

### 2. Text Organization

The text is organized into the following sections:

#### FINDINGS
- **Main Findings**: Text for key findings discovered during verification
- **Limitations**: Text for scope limitations and constraints

#### COMPLIANCE
- **UI Act Compliance**: Text for UIF Act and Contributions Act compliance

#### OVERALL_OUTCOMES
- **Positive Outcomes**: Text for successful verification results
- **Negative Outcomes**: Text for failed verification results

#### VERIFICATION_SCOPES
- **Payment Verification**: Text for payment accuracy verification
- **Employment Verification**: Text for employment validity verification
- **Claims Validity**: Text for claims accuracy verification

#### OBJECTIVES
- **Objective 1**: Employer existence verification
- **Objective 2**: Employee validity verification
- **Objective 3**: Payment accuracy verification
- **Objective 4**: Funds reaching beneficiaries verification
- **Objective 5**: Information validity verification

#### MONTHLY_AMOUNTS
- Helper text for monthly amount displays

#### UI_TEXT
- Section headers and descriptions
- Visual indicators and labels

### 3. Editing Text

To edit any text:

1. **Find the relevant section** in the configuration file
2. **Locate the specific text** you want to change
3. **Modify the string** between the quotes
4. **Save the file**
5. **Restart the application** to see changes

### 4. Example Edits

#### Changing a Finding Text
```python
# Before
"finding_1": "• The employer has under-paid xxx employees over all claim periods. The total underpayments amounted to Rxxx."

# After
"finding_1": "• The employer has under-paid 15 employees over all claim periods. The total underpayments amounted to R45,000."
```

#### Adding a New Limitation
```python
# Add to the limitations section
"limitation_4": "• We could not verify the accuracy of employee ID numbers as the employer did not provide original ID documents."
```

#### Modifying Compliance Text
```python
# Before
"yes": "• The employer provided us with the required documents that confirmed their UIF Contributions were accurate & not in arrears."

# After
"yes": "• The employer provided us with the required documents that confirmed their UIF Contributions were accurate and not in arrears."
```

### 5. Text Formatting Guidelines

- **Use bullet points**: Start each text item with "• "
- **Be specific**: Replace placeholders like "xxx" with actual values when possible
- **Maintain consistency**: Keep similar text items formatted consistently
- **Use clear language**: Write in professional, clear language
- **Include context**: Make sure the text provides enough context for users

### 6. Helper Functions

The configuration file includes helper functions to retrieve text:

- `get_finding_text(finding_type, option)` - Get finding text
- `get_compliance_text(compliance_type, option)` - Get compliance text
- `get_overall_outcome_text(outcome_type, option)` - Get outcome text
- `get_verification_scope_text(scope_type, option, index)` - Get verification text
- `get_objective_text(objective_type, option)` - Get objective text
- `get_monthly_amount_helper_text(amount)` - Get monthly amount helper text

### 7. Best Practices

1. **Backup before editing**: Make a backup of the configuration file before making changes
2. **Test changes**: Restart the application and test your changes
3. **Keep it organized**: Maintain the logical structure of the file
4. **Use comments**: Add comments to explain complex text or sections
5. **Version control**: Consider using version control to track changes

### 8. Troubleshooting

If changes don't appear:
1. **Check file syntax**: Ensure the Python file has valid syntax
2. **Restart application**: The application needs to be restarted to load changes
3. **Check file path**: Ensure you're editing the correct file
4. **Check imports**: Verify the import statement in app.py is correct

## File Location

The configuration file is located at:
```
uif_report_generator/
└── config/
    ├── copy_paste_text.py
    └── README.md
```

## Support

If you encounter issues with the configuration file:
1. Check the Python syntax
2. Verify all quotes are properly closed
3. Ensure the file structure matches the expected format
4. Restart the application after making changes
