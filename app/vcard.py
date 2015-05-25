
VCARD_TEMPLATE = """BEGIN:VCARD
N:%(last_name)s;%(first_name)s;;;
ADR;INTL;PARCEL;WORK:;;;%(city)s;;;%(country)s
EMAIL;INTERNET:%(email)s
ORG:%(org)s
TEL;CELL:%(mobile)s
TITLE:%(title)s
END:VCARD"""


def make_vCard(first_name, last_name, org, title, email, city, country, mobile='N/A'):
    user_data = {'first_name': first_name,
                 'last_name': last_name,
                 'org': org,
                 'title': title,
                 'email': email,
                 'city': city,
                 'country': country,
                 'mobile': mobile}
    return VCARD_TEMPLATE % user_data


if __name__ == "__main__":
    card = make_vCard('Arnaud', 'Sahuguet',
        'The Governance Lab', 'Chief Technology Officer', 'arnaud@thegovlab.org',
        'New York City', 'United States', '+1 646 246 0942')
    print card
