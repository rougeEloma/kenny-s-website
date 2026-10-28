# Legal pages content. Each text is an (English, French) pair: English is written in the page,
# French goes into i18n/fr.json so the FRA | ENG switch translates it.
UPDATED = "26 October 2026"

COMMON = [
    ("Legal", "Mentions légales"),
    ("Last updated", "Dernière mise à jour"),
    ("On this page", "Sur cette page"),
    ("Email", "E-mail"),
    ("Phone", "Téléphone"),
    ("Head office", "Siège social"),
    ("Back to top", "Haut de page"),
]

TERMS = dict(
    file="terms-and-conditions.html",
    crumb=("Terms & conditions", "Conditions générales"),
    title=("Terms & conditions", "Conditions générales"),
    meta_title=("Terms & conditions | Kenny's International", "Conditions générales | Kenny's International"),
    desc=("Terms and conditions for using the Kenny's International website.",
          "Conditions générales d'utilisation du site de Kenny's International."),
    intro=("The rules for using the Kenny's International website. Please read them before browsing.",
           "Les règles d'utilisation du site de Kenny's International. Merci de les lire avant de naviguer."),
    sections=[
        (("About these terms", "À propos de ces conditions"), [
            ("p", "This website is operated by Kenny's International (Kenny's Group), whose head office is at 124 Boulevard du 30 Juin, Gombe, Kinshasa, Democratic Republic of the Congo.",
                  "Ce site est édité par Kenny's International (Kenny's Group), dont le siège social se situe au 124 Boulevard du 30 Juin, Gombe, Kinshasa, République démocratique du Congo."),
            ("p", "By using this website, you accept these terms and conditions. If you do not accept them, please do not use the website.",
                  "En utilisant ce site, vous acceptez les présentes conditions générales. Si vous ne les acceptez pas, merci de ne pas utiliser le site."),
        ]),
        (("Purpose of the website", "Objet du site"), [
            ("p", "This website presents Kenny's Group, the brands we distribute, our stores and our news. It is for information only.",
                  "Ce site présente Kenny's Group, les marques que nous distribuons, nos magasins et nos actualités. Il a une vocation purement informative."),
            ("p", "No products are sold online. All purchases are made in our stores and are governed by the conditions of sale in force in each store.",
                  "Aucun produit n'est vendu en ligne. Tous les achats se font en magasin et sont régis par les conditions de vente en vigueur dans chaque magasin."),
        ]),
        (("Information on brands, products and stores", "Informations sur les marques, produits et magasins"), [
            ("p", "We take care to keep the information on this website accurate and up to date. Opening hours, addresses, brands and product availability may change without notice and can vary from one store to another.",
                  "Nous veillons à ce que les informations de ce site soient exactes et à jour. Les horaires, adresses, marques et la disponibilité des produits peuvent changer sans préavis et varier d'un magasin à l'autre."),
            ("p", "Photos are for illustration only. Please contact the store to confirm a product's availability before you visit.",
                  "Les photos sont présentées à titre d'illustration. Merci de contacter le magasin pour confirmer la disponibilité d'un produit avant votre visite."),
        ]),
        (("Intellectual property", "Propriété intellectuelle"), [
            ("p", "The content of this website (texts, photos, videos, layout and the Kenny's logo) belongs to Kenny's International or is used with the permission of its owners.",
                  "Le contenu de ce site (textes, photos, vidéos, mise en page et logo Kenny's) appartient à Kenny's International ou est utilisé avec l'autorisation de ses propriétaires."),
            ("p", "Brand names and logos shown on this website belong to their respective owners. They appear here because Kenny's Group distributes these brands or operates their stores as a franchise partner.",
                  "Les noms et logos de marques présentés sur ce site appartiennent à leurs propriétaires respectifs. Ils y figurent parce que Kenny's Group distribue ces marques ou exploite leurs magasins en tant que franchisé."),
            ("p", "You may not copy, reproduce or reuse any of this content without our prior written permission.",
                  "Toute copie, reproduction ou réutilisation de ce contenu sans notre autorisation écrite préalable est interdite."),
        ]),
        (("Using the website", "Utilisation du site"), [
            ("p", "You agree to use this website lawfully. In particular, you must not:",
                  "Vous vous engagez à utiliser ce site de manière licite. En particulier, vous ne devez pas :"),
            ("ul", [
                ("try to disrupt the website or access areas that are not meant for you, including the staff area;",
                 "tenter de perturber le site ou d'accéder à des espaces qui ne vous sont pas destinés, y compris l'espace réservé au personnel ;"),
                ("send false, offensive or unsolicited messages through the contact form;",
                 "envoyer des messages faux, offensants ou non sollicités via le formulaire de contact ;"),
                ("use the website's content for commercial purposes without our permission.",
                 "utiliser le contenu du site à des fins commerciales sans notre autorisation."),
            ]),
        ]),
        (("Links to other websites", "Liens vers d'autres sites"), [
            ("p", "This website links to other websites, such as our social media pages, Google Maps and our brands' websites. We have no control over these websites and are not responsible for their content or their privacy practices.",
                  "Ce site contient des liens vers d'autres sites, comme nos réseaux sociaux, Google Maps et les sites de nos marques. Nous n'avons aucun contrôle sur ces sites et ne sommes pas responsables de leur contenu ni de leurs pratiques en matière de confidentialité."),
        ]),
        (("Liability", "Responsabilité"), [
            ("p", "The website is provided as it is. We do our best to keep it available and free of errors, but we cannot guarantee that it will always be available, uninterrupted or error-free.",
                  "Le site est fourni en l'état. Nous faisons de notre mieux pour qu'il soit disponible et sans erreur, mais nous ne pouvons garantir qu'il soit toujours accessible, sans interruption ni erreur."),
            ("p", "To the extent permitted by law, Kenny's International is not liable for any loss or damage resulting from the use of this website or from information found on it.",
                  "Dans les limites permises par la loi, Kenny's International ne saurait être tenue responsable de tout dommage résultant de l'utilisation de ce site ou des informations qui y figurent."),
        ]),
        (("Personal data", "Données personnelles"), [
            ("p", "How we handle the personal data you share with us is explained in our privacy policy.",
                  "La manière dont nous traitons les données personnelles que vous nous communiquez est expliquée dans notre politique de confidentialité."),
            ("link", "privacy-policy.html", "Read the privacy policy", "Lire la politique de confidentialité"),
        ]),
        (("Changes to these terms", "Modification des conditions"), [
            ("p", "We may update these terms at any time. The date at the top of this page shows when they were last changed. Continuing to use the website after a change means you accept the updated terms.",
                  "Nous pouvons modifier ces conditions à tout moment. La date en haut de cette page indique leur dernière mise à jour. Continuer à utiliser le site après une modification vaut acceptation des conditions mises à jour."),
        ]),
        (("Governing law", "Droit applicable"), [
            ("p", "These terms are governed by the laws of the Democratic Republic of the Congo. Any dispute that cannot be settled amicably will be brought before the competent courts of Kinshasa.",
                  "Les présentes conditions sont régies par le droit de la République démocratique du Congo. Tout litige qui ne pourrait être réglé à l'amiable sera porté devant les tribunaux compétents de Kinshasa."),
        ]),
        (("Contact us", "Nous contacter"), [
            ("p", "For any question about these terms, you can reach us here:",
                  "Pour toute question concernant ces conditions, vous pouvez nous joindre ici :"),
            ("contact",),
        ]),
    ],
)

PRIVACY = dict(
    file="privacy-policy.html",
    crumb=("Privacy policy", "Politique de confidentialité"),
    title=("Privacy policy", "Politique de confidentialité"),
    meta_title=("Privacy policy | Kenny's International", "Politique de confidentialité | Kenny's International"),
    desc=("How Kenny's International collects, uses and protects your personal data.",
          "Comment Kenny's International collecte, utilise et protège vos données personnelles."),
    intro=("What personal data we collect through this website, why we collect it and how we protect it.",
           "Les données personnelles que nous collectons via ce site, pourquoi nous les collectons et comment nous les protégeons."),
    sections=[
        (("Who we are", "Qui sommes-nous"), [
            ("p", "This website is operated by Kenny's International (Kenny's Group), head office at 124 Boulevard du 30 Juin, Gombe, Kinshasa, Democratic Republic of the Congo. We are responsible for the personal data collected through it.",
                  "Ce site est édité par Kenny's International (Kenny's Group), dont le siège social se situe au 124 Boulevard du 30 Juin, Gombe, Kinshasa, République démocratique du Congo. Nous sommes responsables des données personnelles collectées par son intermédiaire."),
        ]),
        (("What we collect", "Les données que nous collectons"), [
            ("p", "You can browse this website without creating an account or giving us any personal information. We only collect:",
                  "Vous pouvez consulter ce site sans créer de compte ni nous communiquer d'informations personnelles. Nous collectons uniquement :"),
            ("ul", [
                ("what you send through the contact form: your name, email address, phone number (optional), the topic you choose and your message;",
                 "ce que vous envoyez via le formulaire de contact : votre nom, votre adresse e-mail, votre numéro de téléphone (facultatif), le sujet choisi et votre message ;"),
                ("what you share when you email or call us;",
                 "ce que vous nous communiquez lorsque vous nous écrivez ou nous appelez ;"),
                ("technical data recorded automatically by our servers, such as your IP address, browser type, the pages you visit and the date and time of your visit;",
                 "les données techniques enregistrées automatiquement par nos serveurs, comme votre adresse IP, le type de navigateur, les pages consultées ainsi que la date et l'heure de votre visite ;"),
                ("your language choice (FRA or ENG), which is saved in your own browser only.",
                 "votre choix de langue (FRA ou ENG), enregistré uniquement dans votre propre navigateur."),
            ]),
            ("p", "We never ask for payment details on this website.",
                  "Nous ne vous demandons jamais de coordonnées bancaires sur ce site."),
        ]),
        (("Why we use it", "Pourquoi nous les utilisons"), [
            ("ul", [
                ("to answer your message and follow up on your request;",
                 "pour répondre à votre message et assurer le suivi de votre demande ;"),
                ("to keep the website secure and working properly;",
                 "pour assurer la sécurité et le bon fonctionnement du site ;"),
                ("to meet our legal obligations.",
                 "pour respecter nos obligations légales."),
            ]),
            ("p", "We do not sell your personal data, and we do not send you marketing messages unless you ask us to.",
                  "Nous ne vendons pas vos données personnelles et nous ne vous envoyons pas de messages commerciaux sans votre demande."),
        ]),
        (("Cookies and similar technologies", "Cookies et technologies similaires"), [
            ("p", "This website does not use advertising or audience-measurement cookies.",
                  "Ce site n'utilise pas de cookies publicitaires ni de mesure d'audience."),
            ("ul", [
                ("Your language choice is stored in your browser so the website remembers it on your next visit. You can clear it at any time from your browser settings.",
                 "Votre choix de langue est conservé dans votre navigateur afin que le site s'en souvienne lors de votre prochaine visite. Vous pouvez l'effacer à tout moment depuis les réglages de votre navigateur."),
                ("The staff area uses a strictly necessary session cookie, only for authorised Kenny's staff who sign in.",
                 "L'espace réservé au personnel utilise un cookie de session strictement nécessaire, uniquement pour les membres autorisés du personnel de Kenny's qui s'y connectent."),
                ("The website's fonts are loaded from Google Fonts, and the contact page shows a Google Maps map. When these load, Google receives your IP address and may set its own cookies, under Google's privacy policy.",
                 "Les polices du site sont chargées depuis Google Fonts et la page contact affiche une carte Google Maps. Lors de leur chargement, Google reçoit votre adresse IP et peut déposer ses propres cookies, conformément à sa politique de confidentialité."),
            ]),
        ]),
        (("Who we share it with", "Avec qui nous les partageons"), [
            ("p", "Your data is handled by Kenny's staff who need it to answer you. We only share it with:",
                  "Vos données sont traitées par les membres du personnel de Kenny's qui en ont besoin pour vous répondre. Nous les partageons uniquement avec :"),
            ("ul", [
                ("the companies that host our website and deliver our emails, which process it on our behalf;",
                 "les sociétés qui hébergent notre site et acheminent nos e-mails, qui les traitent pour notre compte ;"),
                ("Google, for the fonts and map described above;",
                 "Google, pour les polices et la carte mentionnées ci-dessus ;"),
                ("the authorities, when the law requires it.",
                 "les autorités, lorsque la loi l'exige."),
            ]),
            ("p", "Some of these providers may store data outside your country. We only work with providers that protect it appropriately.",
                  "Certains de ces prestataires peuvent stocker des données en dehors de votre pays. Nous ne travaillons qu'avec des prestataires qui les protègent de manière appropriée."),
        ]),
        (("How long we keep it", "Durée de conservation"), [
            ("p", "We keep your messages only as long as needed to answer and follow up on your request, unless the law requires us to keep them longer. Server logs are deleted automatically after a short period.",
                  "Nous conservons vos messages uniquement le temps nécessaire pour répondre à votre demande et en assurer le suivi, sauf si la loi nous impose de les conserver plus longtemps. Les journaux des serveurs sont supprimés automatiquement après une courte période."),
        ]),
        (("How we protect it", "Comment nous les protégeons"), [
            ("p", "We take reasonable technical and organisational measures to protect your data, including encrypted connections and access limited to authorised staff. No method of transmission over the internet is completely secure, but we work to keep your data safe.",
                  "Nous prenons des mesures techniques et organisationnelles raisonnables pour protéger vos données, notamment des connexions chiffrées et un accès limité au personnel autorisé. Aucune transmission sur internet n'est totalement sûre, mais nous veillons à la sécurité de vos données."),
        ]),
        (("Your rights", "Vos droits"), [
            ("p", "You can ask us at any time to:",
                  "Vous pouvez à tout moment nous demander :"),
            ("ul", [
                ("see the personal data we hold about you;",
                 "d'accéder aux données personnelles que nous détenons à votre sujet ;"),
                ("correct it if it is wrong;",
                 "de les rectifier si elles sont inexactes ;"),
                ("delete it, or stop using it.",
                 "de les supprimer ou de cesser de les utiliser."),
            ]),
            ("p", "To do so, email us at the address below. We will reply as soon as possible.",
                  "Pour cela, écrivez-nous à l'adresse ci-dessous. Nous vous répondrons dans les meilleurs délais."),
        ]),
        (("Children", "Enfants"), [
            ("p", "This website is not intended for children, and we do not knowingly collect their personal data.",
                  "Ce site ne s'adresse pas aux enfants et nous ne collectons pas sciemment leurs données personnelles."),
        ]),
        (("Changes to this policy", "Modification de cette politique"), [
            ("p", "We may update this policy from time to time. The date at the top of this page shows when it was last changed.",
                  "Nous pouvons mettre à jour cette politique de temps à autre. La date en haut de cette page indique sa dernière mise à jour."),
        ]),
        (("Contact us", "Nous contacter"), [
            ("p", "For any question about your personal data, you can reach us here:",
                  "Pour toute question concernant vos données personnelles, vous pouvez nous joindre ici :"),
            ("contact",),
        ]),
    ],
)


def pairs():
    out = list(COMMON)
    for d in (TERMS, PRIVACY):
        for k in ("crumb", "title", "meta_title", "desc", "intro"):
            out.append(d[k])
        for (h, blocks) in d["sections"]:
            out.append(h)
            for b in blocks:
                if b[0] == "p":
                    out.append((b[1], b[2]))
                elif b[0] == "ul":
                    out.extend(b[1])
                elif b[0] == "link":
                    out.append((b[2], b[3]))
    return out
