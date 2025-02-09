from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Contact
from django.db.models import Q

@api_view(['POST'])
def identify(request):
    email = request.data.get("email")
    phone = request.data.get("phoneNumber")

    # Step 1: Find all matching contacts (either email or phone)
    matching_contacts = Contact.objects.filter(
        Q(email=email) | Q(phoneNumber=phone)
    )

    if matching_contacts.exists():
        # Find the primary contact
        primary_contact = None
        all_contacts = set()
        emails = set()
        phoneNumbers = set()
        secondary_ids = []

        for contact in matching_contacts:
            all_contacts.add(contact)
            emails.add(contact.email)
            phoneNumbers.add(contact.phoneNumber)

            if contact.linkPrecedence == "primary":
                if not primary_contact or contact.createdAt < primary_contact.createdAt:
                    primary_contact = contact

        # Mark all other contacts as secondary and link them
        for contact in all_contacts:
            if contact != primary_contact and contact.linkPrecedence == "primary":
                contact.linkPrecedence = "secondary"
                contact.linkedId = primary_contact
                contact.save()
                secondary_ids.append(contact.id)

        # If new info is found, create a secondary contact
        if (email and email not in emails) or (phone and phone not in phoneNumbers):
            new_contact = Contact.objects.create(
                email=email, phoneNumber=phone,
                linkedId=primary_contact, linkPrecedence="secondary"
            )
            secondary_ids.append(new_contact.id)
            emails.add(email)
            phoneNumbers.add(phone)

    else:
        # No contact found, create a new primary contact
        new_contact = Contact.objects.create(email=email, phoneNumber=phone, linkPrecedence="primary")
        return Response({
            "contact": {
                "primaryContatctId": new_contact.id,
                "emails": [email] if email else [],
                "phoneNumbers": [phone] if phone else [],
                "secondaryContactIds": []
            }
        })

    return Response({
        "contact": {
            "primaryContatctId": primary_contact.id,
            "emails": list(emails),
            "phoneNumbers": list(phoneNumbers),
            "secondaryContactIds": secondary_ids
        }
    })
