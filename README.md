## Carrier Support

MPTracker currently only supports GlobKurier.

During development, I explored integrating directly with major carriers such as USPS and FedEx. Many official carrier APIs require business-oriented registration, additional account verification, or production approval before tracking APIs can be used. GlobKurier provided an accessible tracking service that allowed me to build and test the application's architecture without those barriers.

The application was designed with a modular tracker architecture, making it straightforward to add additional carrier integrations in the future as API access becomes available.

> Hours spent fighting carrier developer portals: ~8