from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Contact
from django.db.models import Q


@api_view(["POST"])
def identify(request):
    email = request.data.get("email")
    phone = request.data.get("phoneNumber")

    matching_contacts = Contact.objects.filter(Q(email=email) | Q(phoneNumber=phone))

    if matching_contacts.exists():
        primary_contacts = list(matching_contacts.filter(linkPrecedence="primary"))

        primary_contact = min(primary_contacts, key=lambda c: c.createdAt)

        secondary_ids = []
        emails = set(matching_contacts.values_list("email", flat=True))
        phoneNumbers = set(matching_contacts.values_list("phoneNumber", flat=True))

        for contact in primary_contacts:
            if contact != primary_contact:
                contact.linkPrecedence = "secondary"
                contact.linkedId = primary_contact
                contact.save()
                secondary_ids.append(contact.id)

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
