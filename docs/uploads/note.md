`note` creates a new note in SysReptor.

## Examples
```bash title="Upload notes"
echo "*Upload me*" | reptor note  # Appends to "Uploads" note
echo "*Upload me*" | reptor note --force  # Force unlock note
echo "*Upload me*" | reptor note --notename "My Note"  # Custom notename
```

## Usage
```
--8<-- "docs/cli/help-messages/note"
```
