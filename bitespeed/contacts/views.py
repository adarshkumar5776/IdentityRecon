from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Contact
from django.db.models import Q


@api_view(["POST"])
def identify(request):
    """
    Identify and consolidate customer contact information based on email and phone number.

    This endpoint processes incoming contact details and ensures they are correctly linked 
    within the database, maintaining a single primary contact and marking others as secondary.

    Steps:
    1. If an existing contact with the given email or phone number exists, it retrieves all related contacts.
    2. Identifies the oldest primary contact and converts newer primary contacts to secondary.
    3. If new information (email/phone) is provided, a secondary contact is created and linked to the primary.
    4. If no matching contact is found, a new primary contact is created.
    
    Request:
        {
            "email": "example@example.com",
            "phoneNumber": "1234567890"
        }

    Response:
        {
            "contact": {
                "primaryContatctId": <primary_contact_id>,
                "emails": [<email_1>, <email_2>, ...],
                "phoneNumbers": [<phone_1>, <phone_2>, ...],
                "secondaryContactIds": [<secondary_id_1>, <secondary_id_2>, ...]
            }
        }

    Args:
        request (Request): The HTTP POST request containing `email` and/or `phoneNumber`.

    Returns:
        Response: JSON response with consolidated contact details.
    """

    email = request.data.get("email")
    phone = request.data.get("phoneNumber")

    # Fetch all contacts that match the given email or phone number
    matching_contacts = Contact.objects.filter(Q(email=email) | Q(phoneNumber=phone))

    if matching_contacts.exists():
        # Retrieve all primary contacts from the matching results
        primary_contacts = list(matching_contacts.filter(linkPrecedence="primary"))

        # Determine the oldest primary contact
        primary_contact = min(primary_contacts, key=lambda c: c.createdAt)

        secondary_ids = []
        emails = set(matching_contacts.values_list("email", flat=True))
        phoneNumbers = set(matching_contacts.values_list("phoneNumber", flat=True))

        # Convert other primary contacts to secondary and link them
        for contact in primary_contacts:
            if contact != primary_contact:
                contact.linkPrecedence = "secondary"
                contact.linkedId = primary_contact
                contact.save()
                secondary_ids.append(contact.id)

        # Create a new secondary contact if new information is provided
        if (email and email not in emails) or (phone and phone not in phoneNumbers):
            new_contact = Contact.objects.create(
                email=email,
                phoneNumber=phone,
                linkedId=primary_contact,
                linkPrecedence="secondary",
            )
            secondary_ids.append(new_contact.id)
            emails.add(email)
            phoneNumbers.add(phone)

    else:
        # No existing contact found, create a new primary contact
        new_contact = Contact.objects.create(
            email=email, phoneNumber=phone, linkPrecedence="primary"
        )
        return Response(
            {
                "contact": {
                    "primaryContatctId": new_contact.id,
                    "emails": [email] if email else [],
                    "phoneNumbers": [phone] if phone else [],
                    "secondaryContactIds": [],
                }
            }
        )

    return Response(
        {
            "contact": {
                "primaryContatctId": primary_contact.id,
                "emails": list(filter(None, emails)),
                "phoneNumbers": list(filter(None, phoneNumbers)),
                "secondaryContactIds": secondary_ids,
            }
        }
    )
