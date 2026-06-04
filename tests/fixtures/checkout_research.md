# Checkout Flow UX Research — Final Report

## Research Questions

- Why do users abandon the checkout flow before completing a purchase?
- What friction points exist between cart and payment confirmation?
- How do users perceive trust signals during payment entry?

## Participants

12 participants (n=12): 6 frequent online shoppers, 4 occasional buyers, 2 first-time users.
Recruited via screener; ages 25–54; mix of mobile and desktop users.

## Key Findings

- 68% of participants cited unexpected shipping costs as the primary abandonment trigger; this surprised them on the final review screen
- Users struggled to locate the promo code field; 5 of 12 gave up applying discounts before completing purchase
- Trust signals (padlock icon, card logos) were noticed by only 3 participants on mobile — the icons rendered below the fold
- The estimated delivery date was the most frequently re-read element across all sessions, suggesting high uncertainty
- First-time users expressed strong hesitation at the account-creation gate; all preferred guest checkout

## Recommendations

- Move shipping cost estimate earlier — display on cart page before users reach checkout
- Reposition the promo code field adjacent to the order summary, not buried in a collapsed accordion
- Increase trust signal visibility on mobile: raise the security badge above the payment form fold
- Offer guest checkout as the default path with an opt-in account creation post-purchase

## Limitations

- Sample skewed toward urban, higher-income users — rural and low-income checkout behaviour not represented
- Testing conducted on staging environment; live production latency may affect perception
- Sessions were moderated; unmoderated behaviour may differ

## Next Steps

- Conduct unmoderated usability testing with a revised prototype addressing shipping cost placement
- A/B test guest-first vs account-first checkout gate
- Follow up with quantitative survey (n≥300) to validate abandonment drivers at scale
