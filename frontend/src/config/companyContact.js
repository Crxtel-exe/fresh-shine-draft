// ===========================================================================
//  COMPANY CONTACT DETAILS  ---  THIS IS THE ONE PLACE TO EDIT THEM
// ===========================================================================
//
//  The "Contact Admin" button on the My Bookings page shows exactly these
//  three details and nothing else: phone number, email address, and Facebook.
//
//  TO CHANGE YOUR CONTACT INFORMATION, EDIT THE THREE VALUES BELOW:
//    - phone     (the company phone number)
//    - email     (the company email address)
//    - facebook  (the company Facebook page)
//
//  Each of those three lines is marked with "<-- EDIT THIS LINE". Change only
//  the text inside the quotes. Do not rename the keys.
// ===========================================================================

export const COMPANY_CONTACT = {
  phone: '0917 123 4567', // <-- EDIT THIS LINE: company phone number
  email: 'hello@sparkleclean.ph', // <-- EDIT THIS LINE: company email address
  facebook: 'facebook.com/sparklecleanph', // <-- EDIT THIS LINE: company Facebook page
}

/**
 * The company contact details as a list, ready for the Contact Admin modal.
 * Each entry becomes one labelled row. Keep this in sync with the object above
 * if you add or remove a detail.
 */
export function companyContactRows() {
  const { phone, email, facebook } = COMPANY_CONTACT
  return [
    { key: 'phone', label: 'Phone', value: phone, href: `tel:${phone.replace(/\s/g, '')}` },
    { key: 'email', label: 'Email', value: email, href: `mailto:${email}` },
    {
      key: 'facebook',
      label: 'Facebook',
      value: facebook,
      
      href: /^https?:\/\//i.test(facebook) ? facebook : `https://${facebook}`,
    },
  ].filter((row) => row.value) // skip any detail left blank
}
