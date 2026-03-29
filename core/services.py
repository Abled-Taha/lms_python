def post_issue_actions(issue_record):
    """
    Handles non-database tasks after a book is successfully issued.
    """
    # 1. TODO: Send Email to issue_record.borrower_email
    # 2. TODO: Send SMS/WhatsApp to issue_record.borrower_phone
    # 3. TODO: Log activity for audit trail
    print(f"Service triggered for {issue_record.borrower_name}")
    pass