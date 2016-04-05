<!--
# Annalist: a practical tool for creating, managing and charing evolving linked data
-->

<!--
## Abstract

Annalist is a software system that makes it easy for individuals and small groups to reap the benefits of using RDF linked data. It presents a flexible web interface for creating, editing and browsing data that can be consumed by other linked data applications, without requiring the user to be familiar with minutiae of the RDF model or syntax, or to perform any programming, HTML coding or prior configuration.

@@expand
-->

# Introduction

In a blog post based on an 2013 ESWC keynote presentation, Karger\cite{Karger2013a} argues that a primary feature of Semantic Web applications should be to accommodate evolving data: "A Semantic Web application is one whose schema is expected to change".
He also argues: "The current state of tools for end users to capture, communicate, and manage their information is *terrible*".
<!--
Describing "Related Worksheets", Bakke *et al*\cite{bakke2011} discuss the "cost-usability gap" between applications and other tools for information workers, and suggest a generic interface for handling structured data.
-->

Annalist ("keeper of records") is a linked data notebook, a software system for creating, editing and managing RDF\cite{w3c-rdf11-concepts} linked data, which attempts to address some of the problems noted by Karger, by allowing the structure of stored data to evolve with understanding of requirements and the nature of the available data.  Its primary aim is to enable individual users and small groups to reap the benefits of creating and using linked data; i.e. to create data that can be shared, evolved and re-mixed with other data on the web.

Annalist is application-agnostic, but has been developed to address data management for small research groups lacking capacity for web site development. It aims to be: easy-to-use, without programming; flexible, allowing structure to be crystallised around available data; sharable, facilitating collaboration with local and remote colleagues; and re-mixable, for combining locally created data with community resources.  Annalist also "scratches an itch" as a tool for web-based personal information management and sharing.

While supporting contribution to linked data at web scale, Annalist's design assumes that individual datasets fit comfortably in the available RAM and local file system of a modern personal computer.  It is not a general-purpose RDF editor, but approaches data from a perspective rooted in application concepts rather as an RDF graph, and not all RDF structures can be generated or directly managed (this does not preclude linking to arbitrary RDF data).  Finally, it is not a general publishing platform: the presentation of data is oriented towards data management actives, and assume the user is familiar with the content.

Annalist is an open development\footnote{\url{http://oss-watch.ac.uk/resources/odm}}, with source code, design notes and documentation kept in a public Github repository\footnote{\url{https://github.com/gklyne/annalist}}.  There is also a public demonstrator and tutorial\footnote{\url{http://annalist.net/}}.

\Needspace{5\baselineskip}

# Motivation and Requirements

One motivating use case for developing Annalist was FlyTED, a database of *Drosophila* Testis Gene Expression images\cite{zhao2010}\cite{zhao2008}.  Our experiences with FlyTED (summarized in figure \ref{flyted_timeline}) give rise to requirements identified in parentheses, and summarized below.

\begin{figure}[ht]
  \centering
  \includegraphics[scale=0.45,keepaspectratio=true]{FlyTED-timeline.eps}
  \caption{FlyTED database timeline.}
  \label{flyted_timeline}
\end{figure}

The FlyTED database was originally intended to be published using the BioImage Database\cite{shotton2004, catton2006}, which was an early implementation of a database incorporating metadata based on semantic web standards.  Limitations of early RDF and web software tool sets imposed design compromises that eventually led to the BioImage Database software not being sustained. Also, an early version of Open Microscopy Environment (OME)\cite{swedlow2005} was evaluated, but its metadata schema was found to be insufficiently flexible to accommodate the range of annotation information that was required (**R4**, **R5**).  Eventually, a modified version of ePrints repository software\cite{gutteridge2002} was used to publish the gene expression images and associated annotations. Some time after the data were published, a combination of a virtual storage service failure and a backup system configuration error resulted in the running system being lost.  Although the original data remained available, the live data was stored in a relational database file; loss of the publication platform, and lack of available resources to re-apply the ePrints customizations and rebuild the database meant the database was not reinstated (**R8**, **R9**, **R10**).  The loss might have been mitigated if live data had been more easily shared, including via version management systems (**R6**).

Although not large, the FlyTED data were expensive to gather, hence valuable, with each combination of gene and phenotype requiring literature and database searches, statistical analysis, laboratory procedures for sample preparation, microscopic image capture and annotation by a biological expert. Initial input of image annotations used spreadsheets, as the biologists were familiar with these (**R1**, **R3**). During the course of the investigations documented by FlyTED, the terms used to record developmental stages during which genes were active were adjusted to provide better coverage of the observations (**R5**).  Programmatic access to the underlying data was subsequently used to create an exemplar application, OpenFlyData\cite{miles2010}, which provided facilities for search and co-display of gene information across a number of *Drosophila* databases (**R11**).

The FlyTED database was created by a small team of software developers working closely with biologists, but the original intent was to pave the way for tools that biologists could use without developer support (**R1**, **R2**, **R3**). Without the support of developers, the biologists would almost certainly have not gone beyond creating spreadsheets containing their observations, the contents of which cannot easily be cross-referenced with external data sources without prior knowledge of their structure (e.g. which column is used for the FlyBase gene ID?).  In creating the published database, observed genes were cross-referenced with FlyBase\cite{santos2015}, the community database of information about *Drosophila* genes, and annotated using terms compliant with the MISFISHIE standard\cite{deutsch2006} (**R4**, **R7**).

Finally, and not directly related to the FlyTED experience, we also wanted Annalist to be suitable for offline use (e.g. for field work) (**R12**).

\paragraph*{Summary of requirements}

R1
: Ease of use: possible to quickly create a simple collection and start capturing data.

R2
: Ease of use: no programming or HTML coding needed to create a new collection.

R3
: Ease of use: detailed knowledge of RDF and/or OWL not needed to create or edit data.

R4
: Flexibility: choice of RDF vocabulary used in the data.

R5
: Flexibility: possible to define or adapt structure of data as it is collected.

R6
: Sharability: data can be shared between collaborators using a variety of techniques, including online access and offline file copying.

R7
: Remixability: 
use of domain vocabularies or ontologies to facilitate combining with community datasets; 
ability to present data as linkable web resources, and to link to external web resources.

R8
: Portability: possible to move data between live systems; not dependent on a single central service.

R9
: Sustainability of software: data capture, editing and browsing possible using unmodified software.

R10
: Sustainability of data: underlying data stored and exposed using a standard, easily used data format.

R11
: Visible data: underlying data exposed so that functions not provided by the system (e.g. data visualization) can be implemented by independent software.

R12
: Offline working: deployable on a personal computer, allowing work on linked data collections without an Internet connection.

# Related work

As a system for creating and managing data on the web, Annalist enters a crowded space with a wealth of alternatives available. But, despite this, we are unaware of anything that provides the out-of-box capability of Annalist for creating linked data, and meeting the requirements outlined.  Figure \ref{requirements-matrix} gives an overview of systems with respect to the requirements listed above.
Our survey focuses on tools that directly present end-user data management interfaces. There are systems (e.g. Virtuoso, Sesame, Jena, WikiBase, etc.) that are primarily semantic data stores and developer tools that are not covered. Also, tools for data cleaning (e.g. OpenRefine, LODRefine) or middleware that augments existing data (e.g. Poolparty, Sponger) are considered complementary rather than alternatives to Annalist.

\begin{figure}[ht]
  \centering
  \includegraphics[scale=0.45,keepaspectratio=true]{requirements-matrix.eps}
  \caption{Related work overview.}
  \label{requirements-matrix}
\end{figure}

## Semantic Web Systems and Tools

Callimachus\footnote{\url{http://callimachusproject.org}} provides flexible support for sharable linked data, but is a tool for developers rather than end-users. Semantic media wiki\footnote{\url{http://semantic-mediawiki.org}}\cite{volkel2006} is usable without additional development, but is not really suited to desktop deployment, and the data is not amenable to version management or sharing via file sharing. Rauschmayer presented a poster\cite{rauschmayer2008} about the Hyena RDF editor at SemWiki 2008, which appears to envisage similar usage scenarios as Annalist, but does not currently appear to be available as a usable tool. This work is described in Rauschmayer's PhD thesis\cite{rauschmayer2010}, which states that the core idea is to use a central repository for linked information, where Annalist is conceived as being just a small part in a wider linked data infrastructure.  Wikidata\footnote{\url{https://www.wikidata.org/}}, built upon the Wikibase\footnote{url{http://wikiba.se}} data store, acts as central storage for structured data of Wikimedia projects.  It has similarities to Annalist - "items" and "statements" parallel Annalist's Entities and Fields, but the user interface is not customizable and it does not appear to support the creation of data collections independently of Wikipedia and related projects.

There are ontology design tools, such as <!-- Prot\'{e}g\'{e}-->Protege\cite{protege} (including WebProtege), which can be used to create RDF data, but a focus on ontology design leads to a complex interface that is not well suited for end-user creation and management of linked data. Changing the data structure requires an understanding of ontology design.

Piggy Bank\cite{huynh2007piggybank} was developed as a tool for consuming web data, and creating a local RDF store to facilitate navigation and merging data from diverse sources.  The emphasis here was on consuming web data from heterogeneous sources (something that Annalist can facilitate), but not so much on creating linked data for sharing and eventual publication.

Fresnel\cite{pietriga2006fresnel} is an RDF vocabulary for controlling presentation of RDF, for which Annalist uses home-spun terms.  The development of Annalist focused initially on creating a user interface to create linked data without knowledge of HTML or RDF (requirements R2, R3), and the vocabulary needed to describe the presentation emerged from this approach. With the technical requirements now established in running code, evaluating a retro-fit of Fresnel could be a topic for further work.  RDForms\footnote{\url{http://rdforms.org/}} ("RDF Forms") is a JavaScript library supporting a declarative description of views for editing and presenting RDF, whose interface appears to have some aspects in common with Annalist. But RDForms is a developer tool, and not something that can be used without programming.

<!-- % \footnote{\url{http://protege.stanford.edu}} -->

One use for Annalist has been to create additional information, or annotations, related to web pages (e.g., see section \ref{accommodation-search} below).  Pundit\footnote{\url{http://thepund.it}} is positioned as a semantic web annotation tool for research, capable of performing faceted search over annotated web pages\footnote{\url{http://eswcdemo.gramsciproject.org}}. It appears to be able to create linked data annotations, but it is not clear if it can create free-standing linked datasets, or how easily the annotations created can be exported and/or consumed by other applications. Another annotation tool is Domeo\footnote{\url{http://swan.mindinformatics.org}}\cite{ciccarese2012}: this, too, can create RDF annotations of online documents, but does not appear to create free-standing data.

## Data sharing platforms

Figshare\footnote{\url{http://figshare.com}} is a a proprietary web platform for research data sharing that is well-suited for sharing research papers, supporting data and other materials, but does not of itself provide support for creating re-mixable linked data. ResearchSpace\footnote{\url{http://www.researchspace.org}} is developing "a collaborative environment for humanities and cultural heritage research using knowledge representation and Semantic Web technologies", sharing some goals with Annalist, but specialized for cultural heritage by building specifically on CIDOC CRM\cite{cidoc-crm62}.

The Database Wiki\cite{buneman2011} is another project to provide a gen\-eric, collaborative, user-friendly interface over structured data. In this case, the underlying data is XML rather than RDF, and there is less emphasis on linking with external data. This project is informed by Form Lenses\cite{rajkumar2013}, a principled approach to mapping between stored data and a presented user interface, based on Applicative Functors\cite{mcbride2008}, which offer a possible avenue for future work with Annalist.

Histcross\footnote{\url{https://github.com/mkalus/histcross}}\cite{kalus2007} was a semantic database of historical data, subsequently replaced by Segrada\footnote{\url{http://www.segrada.org}}, apparently with many similar goals to Annalist, but does not work with linked data so would not readily participate in a wider network of data. 

## Spreadsheets and desktop databases

Regular spreadsheets (Excel, Open Office, etc.) are very popular for research and personal information management, offering flexibility, ease of use and sharing (e.g. via CSV), but do not easily support combining data from different sources, do not provide direct web access to the underlying data, and are not particularly well suited for use with version control systems. Rightfield\cite{wolstencroft2012} is a tool that augments spreadsheets to facilitate entry of semantically constrained terms, and as such goes some way to addressing the remixing problems of spreadsheet data, but does not really lend itself to creating multiple cross-linked linked data structures, and shares other limitations of spreadsheets.

Bakke\cite{bakke2011} reports an an experiment with Related Worksheets that explores the management of multiple relations between worksheets in a desktop application. Their paper clearly explain some problems that Annalist aims to address, and proceeds to evaluate how they can be addressed in a spreadsheet interface. The work suggests user interface designs that might be helpful, but does not of itself provide usable tools for creating linked data.

Desktop databases such as Access\footnote{\url{https://products.office.com/en-us/access}} require some configuration effort before they can be used for capturing data, which in turn are constrained by the relational schema used, and not readily linked with external datasets. 

## Content management systems

Other classes of web application that might be considered for research data management include Content Management Systems (CMSs, such as Wordpress\footnote{\url{https://wordpress.org}} or Drupal\footnote{\url{https://www.drupal.org}}). These require significant development and/or configuration effort to create a data sharing platform, and do not support the full flexibility of RDF linked data. Drupal has built-in RDF support that is layered over an underlying schema, and is not amenable to change without re-working the underlying site configuration. Also, CMSs tend to hide the underlying data from direct view or manipulation, rather than exposing it for other applications to use in different ways.

## Electronic Laboratory Notebooks

Annalist in some respects resembles electronic laboratory notebook systems (ELNs). There are many proprietary ELNs that are aimed at commercial research laboratories and as such may be beyond the budget of an individual or small research group. There are also some open source ELNs (e.g. Voegele et al\cite{voegele2013}, elabftw\footnote{\url{http://elabftw.net/}}, LabTrove\cite{frey2013labtrove}. We have not specifically evaluated any of these, but in general they offer a blog-like platform, where textual notes may be augmented with named attribute or tabular data. We are not aware of any ELNs that support web linked data.

<!-- Cerys notes:
    I think LabTrove is attempting to do something similar but perhaps with less structure and with less granularity.

    The blog interface is meant to give the users the most flexible (natural) way to enter their information with limited ways to create structure. The section and key-value pair metadata are the only ways the user has of communicating structure by indicating what type of record it is (section) and adding some properties - for example material: sodium chloride (key value pairs). Other than that LabTrove is automatically adding some basic metadata such as timestamp, author, and version. Each version is a separate object with it's own identifier. There is some automatic linking - the post is linked to the data files added to it, the user defined metadata can be used to group posts that share the same metadata. Templates can be created that help guide the content that the users enter - but apart from the metadata, none of this is structured in such a way that it can be used by internally by LabTrove or by the user. Posts can be linked together by creating a link to another post within a post, but there isn't a way of referencing a part of a post or automatically linking them. 

    In LabTrove a savvy user will be consistent and create their own structure from the user defined metadata, for example they might have posts that represent 'Methods', 'Experiment', and 'Results' by using these values for the section metadata and then use meaningful key-value pairs such as materials or the experiment id that can then be used to group (navigationally link) together these related posts. But there are limitations when the number of posts is high or the amount of metadata is high - and a large percentage users do not use the metadata effectively or even at all. A user doesn't have to give more than a section and the section can be and often is generic or meaningless. In Annalist we are providing the structure - we are making the decision for the user - we can give a complex or a simple structure and there are consequences of doing either! 

    For me the power of Annalist is in being able to *create that structure* and most importantly *making use of the structure* - but I see that currently it requires quite a lot of time and skill to do that. In LabTrove there is limited structure that can be created - but if you have an organised mind you can do that easily. In Annalist you can adapt your structure. This is much more difficult in LabTrove because you have to amend each post to create a structure - this difficulty in being able to change the structure is one of the reasons given by users for why they only use the barest minimum. The perceived benefits do not out weigh the perceived difficulties of 'getting it wrong'.
-->


# Design

<!--
To address the indicated requirements, a number of principles have been adopted that inform the Annalist software design:
-->

Annalist adopts a frame-oriented, or entity-oriented, approach to presenting and storing data, rather than being RDF graph based.  Frames are considered to be easy for people to understand as they model some aspects of human memory patterns\cite{kalus2007}.  schraefel and Karger\cite{karger2006} explore in some depth the presentation of semantic web data in user interactions, and emphasize consideration of “what do we want to do”; in the case of Annalist, what we want to do is create, manage and share linked data on the web.  We observe that when researchers use spreadsheets to create data, it is commonly arranged with a row of information for each of a number of similar entities (e.g. microarray descriptions commonly use a row of values for each of several thousand gene probes).  The frame-based approach has implementation advantages, too: it provides a convenient grouping of data such that the description of each entity is stored as a separate file, assigned a URL, and directly accessed as a web resource.

In discussions with researchers about their preference for using spreadsheets, we were told that one of their reasons is that spreadsheets do not impose *a priori* constraints on what can be entered, making it easy for them to enter data as it becomes available.
Bakke *et al*\cite{bakke2011} also note "When it comes to general editing tasks on tabular data, spreadsheet systems have an advantage even over most tailor-made applications", and advantages of a system that can "allow temporary inconsistencies".
Frey *et al*\cite{frey2013labtrove} also note that semantically aware tools "could be too heavyweight and prescriptive", restricting re-use in other areas.  Annalist adopts a principle that its first task is to make it easy for researchers to capture their data; defining structure is secondary.  Further, there is no attempt to validate data entered, or impose any kind of quality standards: we take a view that validity, quality and refinement are dependent on a context of use\cite{zhao2013}, and as such are usefully applied in such context.

Linked data vocabulary terms are commonly associated with schemas (or ontologies), but we observe that such terms may be adopted independently of any schema.  Annalist supports evolving data initially though addition of terms, even to the extent of taking an unstructured narrative, identifying significant elements, and progressively articulating them using new terms, preferably drawn from existing stable schemas (e.g. sections \ref{the-carolan-guitar} and \ref{smoke}).  A related concern is evolving schemas, which incur changes to terms already used in data. Annalist provides support for supertype URIs in type definitions, and property aliases, which can assist with type and property URI migration; generalization of these features is ongoing.  We have also performed migrations by direct editing of the underlying data; while not an option for non-technical users, it shows that schema evolution can also be assisted by external services.

The requirements for internal data to be exposed to third party applications, and data portability, are addressed by using JSON -- specifically JSON-LD\cite{w3c-json-ld} -- as the primary internal data storage format. JSON-LD conventions allow data to be interpreted as RDF, yet retaining the ease-of-use of JSON, and use by applications that have no knowledge of RDF.  Within the data managed by Annalist, internal links are stored as URI relative references\cite{bernerslee2005uri}, to be resolved against the URL used to access the data, allowing data to be copied from one Annalist deployment to another without changes.  Use of Compact URIs (CURIEs\footnote{\url{http://www.w3.org/TR/curie/}}) for field names and types, with prefixes defined in external JSON-LD context files, allows for more compact, readable and understandable data compared with using full URIs.

\begin{figure}[ht]
  \centering
  \includegraphics[scale=0.36,keepaspectratio=true]{annalist-components.eps}
  \caption{Annalist software components.}
  \label{software_diag}
\end{figure}

Figure \ref{software_diag} shows the main components of the Annalist software.  It is implemented as an HTTP server application, written in Python using the Django\footnote{\url{https://www.djangoproject.com}} software framework. All the essential Annalist application logic is implemented by the server, but there is some limited use of Javascript in the browser to provide a more responsive user interface; the intent here is that Annalist can be used in browser enviroments where Javascript is disabled or unavailable.  The Annalist server software is designed to be deployed locally (on a personal computer), on a private network, or on a publicly accessible host.

\begin{figure}[ht]
  \centering
  \includegraphics[scale=0.36,keepaspectratio=true]{screenshot_view_data.png}
  \caption{Annalist data record view example.}
  \label{view_data}
\end{figure}
    <!-- \hspace*{-1cm} -->

\begin{figure}[ht]
  \centering
  \includegraphics[scale=0.35,keepaspectratio=true]{screenshot_edit_view.png}
  \caption{Annalist record edit view example.}
  \label{edit_view}
\end{figure}

\begin{figure}[ht]
  \centering
  \hspace*{-1cm}
  \includegraphics[scale=0.35,keepaspectratio=true]{screenshot_list_performances_crop.png}
  \caption{Annalist list view example.}
  \label{list_views}
\end{figure}

At the heart of Annalist is a dynamic web-page creator and form rendering engine that combines user data with a form description to create an HTML web page. Figure \ref{view_data} is an example of data viewed using Annalist.
The underlying JSON-LD data can be accessed by web retrieval, either via Annalist, or a suitably configured web server; the file layout is designed to preserve relative references.  This helps to ensure that access to the data is not dependent on the health of the Annalist service.  A goal is to allow user data to be stored on the web, separately from the Annalist service itself, though there remain some access control details to be resolved to make this a reality.

Figure \ref{edit_view} shows an example of the Annalist data editing interface. It actually shows a form used for editing the definition of a form description, so is self-referential: the labels of the fields on the left of the page are echoed in the list of field descriptions at the bottom of the page. 

Figure \ref{list_views} shows an excerpt from a listing of records. These examples illustrate main kinds of display provided by Annalist: a detailed view of a single record, which may be an editing view or a view-only display, and a summary list of multiple records.  Further examples of the Annalist user interface can be found in the Annalist tutorial document\footnote{\url{http://annalist.net/documents/tutorial/main}}. 

\begin{figure}[ht]
  \centering
  \includegraphics[scale=0.42,keepaspectratio=true]{annalist-concepts.eps}
  \caption{Annalist internal data model.}
  \label{data_model}
\end{figure}

Like the user data, form descriptions and other configuration data are stored as JSON-LD files, and are editable through the Annalist web interface. This makes Annalist self-maintaining, in the sense that there is no separate configuration interface or other mechanism needed to define data types, storage structures, or their presentation.

Data are organized as illustrated in figure \ref{data_model}.  At the top level is an Annalist ***Site***, which is associated with an Internet host (or `localhost` for desktop deployment).  Site data is grouped into free-standing ***Collections***, which contain user data, and metadata to define its structure and presentation.

The data are stored in ***Data records***, each of which is presumed to describe some entity, and corresponds to an addressable web resource or file (each having a distinct URL).  ***Record types*** correspond to the type of entity described, and are used to combine similar entities for user presentation (e.g. in lists), and also in the underlying data storage (e.g. entities of different types are stored in different directories or storage containers). ***Record views*** define forms used for creating, editing or viewing data records; ***Record lists*** define presentation of multiple entities for browsing. ***Field definitions*** are referenced by *record views* and *record lists*, and control the internal representation and presentation of record component values.  ***Field groups*** are used to group fields for various purposes, e.g. to define repeated groups of fields. URIs used for type and property URIs are contained in the record type, field and view definitions, and may be drawn from existing ontologies, or local ad/hoc identifiers with potential to adopt existing vocabularies as correspondences are determined.

Access control is managed in two parts: authentication is by a third-party identity provider (IDP) using OpenID Connect\footnote{\url{http://openid.net/connect/}} returning an authenticated email address. Annalist has been tested to date using the Google login service\footnote{\url{https://developers.google.com/identity/protocols/OpenIDConnect}}. 
Access control is handled by permissions stored as Annalist records, which are defined and applied on a per-collection basis, with fall-back to site-wide permissions. Permissions required for access may depend on record type (e.g. ADMIN permission required to access the permission records), and in future this might be used for finer-grained control.

\Needspace{5\baselineskip}

# Applications

Annalist has been used with several personal and research projects, described below, which have informed its ongoing development. The first example includes a sketch of its implementation to provide insight into use of Annalist, and all can be examined at the URLs given.

## The Carolan Guitar

This is a project of Nottingham University's Mixed Reality Laboratory on "Augmenting a Guitar with its Digital Footprint"\cite{benford2015}, recording its history online in the form of a blog\footnote{\url{http://carolanguitar.com}}. Annalist has been used to create a linked data overlay of this history that links to the blog itself, and also to other key resources that are part of its history\footnote{\url{http://demo.annalist.net/annalist/c/Carolan_Guitar/d/Artifact/Carolan_Guitar/}}. 
This overlay models events (construction, composition, performance and others), people, places, artifacts, materials, musical compositions and more using vocabularies drawn from 
RDFS\cite{w3c-rdf11-schema}, 
CIDOC CRM\cite{cidoc-crm62, Doerr2003}, 
FRBRoo\cite{cidoc-frbroo10}, and
W3C PROV\cite{w3c-prov-o}.

### Carolan Guitar implementation

\begin{figure}[ht]
  \centering
  \includegraphics[scale=0.4,keepaspectratio=true]{Carolan-types.eps}
  \caption{Carolan Guitar description types.}
  \label{carolan_types}
\end{figure}

The Carolan Guitar description is built around the types shown in figure \ref{carolan_types}.  The types `Entity` and `Event` reflect core elements of both PROV (`prov:Entity`, `prov:Activity`) and CIDOC CRM (`crm:E71_Man-Made_Thing`, `crm:E5_Event`) ontologies.  Other, more refined, types are introduced as judged useful to capture the guitar's history.  The Carolan Guitar itself is an instance of `Artifact`, a subtype of `Entity`, which is primarily an instance of the CIDOC CRM type `crm:E24_Physical_Man-Made_Thing`, but is also associated with a number of other types in the type definition\footnote{\url{http://demo.annalist.net/annalist/c/Carolan_Guitar/d/_type/Artifact/type_meta.jsonld}}:

\begin{lstlisting}[language=Java]
{"annal:id":      "Artifact",
 "annal:type":    "annal:Type",
 "rdfs:label":    "A constructed physical entity",
 "rdfs:comment":  "An artifact, such as a musical instrument or some other object.",
 "annal:uri":     "crm:E24_Physical_Man-Made_Thing",
 "annal:supertype_uris": [
   {"annal:supertype_uri": "prov:Entity"},
   {"annal:supertype_uri": "crm:E77_Persistent_Item"},
   {"annal:supertype_uri": "crm:E70_Thing"},
   {"annal:supertype_uri": "crm:E71_Man-Made_Thing"},
   {"annal:supertype_uri": "crm:E18_Physical_Thing"},
   {"annal:supertype_uri": "frbroo:F7_Object"}],
 "annal:type_list": "_list/Artifacts",
 "annal:type_view": "_view/Artifact"}
\end{lstlisting}

The central subject, the Carolan Guitar, is presented using the `Artifact` Record view\footnote{\url{http://demo.annalist.net/annalist/c/Carolan_Guitar/d/_view/Artifact/view_meta.jsonld}}.  This view describes an `Artifact` with an identifier, type, label, description, links to further information, and (central to this application) a list of life events, which correspond to a journal of its history.  

<!--
\begin{lstlisting}[language=Java]
{"annal:id":          "Artifact",
 "annal:type":        "annal:View",
 "rdfs:label":        "Artifact",
 "rdfs:comment":      "Simple view of an artifact",
 "annal:view_fields": [
   {"annal:field_id": "_field/Entity_id", ...},
   {"annal:field_id": "_field/Entity_type", ...},
   {"annal:field_id": "_field/Entity_label", ...},
   {"annal:field_id": "_field/Entity_comment", ...},
   {"annal:field_id": "_field/See_also_r", ...},
   {"annal:field_id": "_field/Event_r", ...}]}
\end{lstlisting}
-->

Information about the Carolan Guitar and its life events are recorded in its description\footnote{\url{http://demo.annalist.net/annalist/c/Carolan_Guitar/d/Artifact/Carolan_Guitar/entity_data.jsonld}}, e.g.:

\begin{lstlisting}[language=Java]
   :
  {"crm:P12i_was_present_at": "Construction/Construction_9"},
  {"crm:P12i_was_present_at": "Performance/First_performance"},
  {"crm:P12i_was_present_at": "Performance/Stairway"},
  {"crm:P12i_was_present_at": "Performance/Hop_jam"},
  {"crm:P12i_was_present_at": "Event/Photo_shoot"},
  {"crm:P12i_was_present_at": "Composition/Catch_the_moment"},
   :
\end{lstlisting}

Here, relative URL references are used to designate life events, each of which may record information about where it took place, entities used, and who was involved in what roles.  Different types of event in the guitar's history (construction, composition, performance, etc.) may also have different information:  a construction event view\footnote{\url{http://demo.annalist.net/annalist/c/Carolan_Guitar/d/_view/Construction/view_meta.jsonld}} may include information about the tools, materials used; a performance view\footnote{\url{http://demo.annalist.net/annalist/c/Carolan_Guitar/d/_view/Performance/view_meta.jsonld}} may include  details of the works performed.

The modeling of the Carolan Guitar's story is by no means complete (if such a thing is ever possible), and some choices of what to include could reasonably be described as arbitrary.  But, using Annalist, the description can be augmented and refined with additional types and more detailed view descriptions as new requirements are encountered.  Indeed, this has already happened several times during its development.


## Smoke: creating an audio-visual poem
\label{smoke}

Procedural Bending is presented in Garrelfs' PhD thesis\cite{garrelfs2015} as a model for discourse about creative processes. It has similarities with the W3C PROV model\cite{w3c-prov-o}, but also some key differences.
Annalist has been used to create a description of the creation of "Smoke"\footnote{\url{http://irisgarrelfs.com/smoke}}, an "experimental documentary come audio-visual poem" about mid 20th-century air pollution in the cities of Pittsburgh and St Louis.
In this case, a semi-structured blog-like journal was created by the artist using Annalist\footnote{\url{http://cream.annalist.net/annalist/c/IG_Philadelphia_Project/}}, together with a Procedural Blend diagram <!--\footnote{\url{http://cream.annalist.net/annalist/c/IG_Philadelphia_Project/d/Image/PB_Illustrator_2/}}--> using the model from Garrelfs' thesis. We worked with the artist to encode the blend diagram as Annalist records, and in the process were able to refine the model to make it more consistently encodable while preserving the original descriptive intent.

[Garrelfs2015]: http://irisgarrelfs.com/thesis
<!--
\footnote{\url{...}}
[Garrelfs2015b]: http://irisgarrelfs.com/smoke
-->


## Chemistry Personas

Chemistry Personas\footnote{\url{http://cream.annalist.net/annalist/c/Chemistry_Personas/}} 
evaluates Annalist as a tool for capturing records of academic researchers in chemistry, and for identifying metadata from these records. It was used to create a set of interfaces for the capture and linking of information about people, organisations, projects, and resources associated with experiments such as plans, materials, equipment, activities, and the experiment records themselves that incorporate linked data.  Designs of the models are based on research information and associated metadata from experiment records, and observed recording practices in chemistry from a range of universities across the world.

Annalist was found to be useful for capturing research records and associated data, with the flexibility to be easily adapted to the needs of different research groups and individual researchers.  We found the generic capability to create specialized interfaces for capturing information allowed us to handle the different requirements of different domains and disciplines. The linked-data aspect is particularly useful in enabling the simple reuse of resources and plans, and inclusion of frequently used information into the research records.


## Canal Cruising Log

The canal cruising log\footnote{\url{http://demo.annalist.net/annalist/c/CruisingLog/}} 
is an example of Annalist used for personal information management. It captures information about narrowboat cruising on the English canal network, with information about daily movements, waterways, places visited, other interesting locations, and maintenance activities performed. It is based on a handwritten log book, and attempts to capture information in searchable form that may be useful when planning waterways travels. The information modelling is *ad hoc* (i.e. uses private vocabulary terms). Using Annalist, it would be quick and easy to revisit and add class URIs from standard ontologies. Property URIs are harder to update, but but work is in progress to support data migration as properties change.

## Accommodation search

The accommodation search collection\footnote{\url{http://demo.annalist.net/annalist/c/Accommodation_search/}} 
is another example of personal information management, this time with a clear real-world outcome. We sought a new home for an elderly relative that would make it easier to provide increasingly-needed levels of support. The web made it easy to find candidate properties, but there were specific requirements (e.g., physical accessibility) not selectable by available search facilities, so we had to filter from a large number of candidate properties; further, good properties would come to market and disappear quickly, so prompt information sharing was needed. Annalist was used to rapidly create a specialised database of candidates, with links to existing property web sites, additional annotations, an an overall scoring of suitability according to our particular requirements. This was shared among family members, and when the ideal property appeared we were able to consult over the details and arrange an early visit.


# Discussion

## Evaluation of requirements

Section \ref{motivation-and-requirements} set out a number of requirements arising mainly from past experiences creating FlyTED.  We now review those requirements against the implemented Annalist applications described in section \ref{applications}.

Requirements **R2** (no programming), **R6** (data sharing), **R9** (use of unmodified software) and **R10** (expose data in a standard format) are demonstrated by all of the implementations described.  Our work on these implementations has repeatedly exploited **R8** (portability of data) and **R12** (offline working) by using a GitHub repository\footnote{\url{https://github.com/ninebynine}} to transfer work-in-progress data between an offline laptop and online servers; this use of Github for data exchange, backup and versioning also demonstrates another aspect of **R10** (sustainability of data).  Annalist's exposure of underlying data (**R11**) is present in all the applications described, but has not been significantly exploited by independent software; this will be tested in future work.

The implementation of *The Carolan Guitar* data has shown extensive use of **R4** and **R7** (choice and mixing of existing RDF vocabularies), combining PROV, CIDOC CRM, FRBRoo and some private terms.  Requirement **R5** (evolution of structure) was used when working through the Carolan Guitar's history, starting with its construction, but in later stages dealing with musical performances and compositions.  

The *The Canal Cruising Log* implementation in particular demonstrates **R3** (not needing knowledge of RDF) as this has been developed without reference to any specific RDF terms or characteristics.  The frame-oriented approach to data presentation appears to be more approachable than requiring users to work with the RDF graph/triple structure (also suggested by Kalus\cite{kalus2007}).  There is one aspect where RDF influences remain visible:  field descriptions must specify a property string in the form of a URI or CURIE that is used to identify an attribute in the data (the effect of which is to constrain the syntax of attribute identifying strings).  

The *Accommodation search* application demonstrates the achievement of **R1** (to quickly create a  collection and start capturing data) as this ephemeral application would never have been realized if it would have taken more than an hour or so to create the collection with some initial data records.

##  Further observations

**Primary storage of data as simple text resources**: 
there is no database or triple store behind Annalist. For locally stored resources, each addressable resource is stored as a single JSON-LD file, and the request URL is mapped to a corresponding filename. The underlying resources may be served directly by a web server without any Annalist deployment being present, which we believe could be a boon for long-term sustainability of research data (e.g., the Annalist demo site\footnote{\url{http://demo.annalist.net/}} also offers links\footnote{\url{http://annalist.net/annalist_sitedata/}} that connect directly to the underlying data). This approach allows collections to be versioned using common version management tools (e.g. git), and shared via version repositories.

**Edit conflicts**: Annalist handles concurrent updates to individual entities by atomic updates. 
There is an unimplemented design for warning when an entity changes during editing. 
Consistency of values between entities is not currently enforced (see section \ref{design}).

**Performance**: the Annalist demonstrator runs on a modestly provisioned virtual machine (1 virtual CPU, 2Gb RAM). We have not undertaken formal measurements, but have not found performance to be a limitation in day-to-day use. This matches our expectation that the underlying Linux file system is very efficient for accessing small files that comprise Annalist collections. Some particular operations perform repeated file accesses, and future work is
planned to optimize these cases.
Planned developments will introduce an index alongside the flat files, probably a triple store, to support efficient search and query over the data.

**Data types for organisation, views to define structure**: 
traditional database systems use data types (or equivalent) both to categorize data records and to associate structure with the data (e.g. a relational table defines the structure of each row in a table). This is less true for schema-free databases (e.g. MongoDB\footnote{\url{https://www.mongodb.com/}}), but even here we may see that structural features such as indexes are associated with what is effectively a data type (e.g. in MongoDB, a "collection"). With Annalist, types are used simply to categorize data records, and the structure of any record is determined by the view (or views) that are used to create or edit it. This means that different views can be used with a record type, according to the context (e.g., considering a person as an employee or as a customer).  (When editing a record with fields not referenced by the view used, those fields are unchanged when the record is saved.)

**Collection portability: URLs and URIs**: 
moving a collection between Annalist deployments means that the URLs used to access records can change. But for some fields, such as type descriptions, we need stable identifiers that don't change with location of the data. The implementation of Annalist recognizes this tension, and distinguishes between URLs used to access and retrieve resources and URIs used to identify them. This goes somewhat against the grain of web wisdom, and in practice the distinction is used quite sparingly, but we believe this illustrates that in pragmatic applications, particularly where there may be copies of the same information in different locations, the distinction may have some value. (This differs from earlier discussions about URNs and URIs\footnote{\url{http://www.w3.org/TR/uri-clarification/}}, in that the distinction is in no way dependent on the URI scheme used: a given HTTP URI may be a URI or URL depending on how it is used.)

**Usability**: we have not yet undertaken formal usability studies, but our experience to date indicates that it is possible to quickly create data managment forms that are usable with no special knowledge or experience. We have found that creating structure and view definitions can become complicated when there are multiple relationships between entity types, and improvements in this area are ongoing.

**Scale**:
Annalist deals with collections of modest size, but through the milieu of the web even such modest collections, in sufficient numbers, may contribute to data at much greater scales.  Tools, like Annalist, that facilitate creation of linked data at local scales may be a key to enabling fully distributed datasets at web scale.


# Further work

The nature of Annalist as a generic tool means there is inevitably far more that could be done than has been achieved to date. Work-in-progress enhancements include: modular type/view definitions, importing definitions from a predefined collection, which we see as allowing end-users to get started even more quickly with generating their own linked data (e.g. using "canned" definitions for bibliographic and provenance information); usability improvements to streamline common data entry tasks (e.g. automatic creation of default views and lists associated with a data type); data migration facilities to assist with applying vocabulary changes to existing data.

Work is currently underway to create an independent front-end for presentation of musical performance data created using Annalist (based on the structures developed for the Carolan Guitar), which we plan to use to develop a demonstration system aimed at enhancing audience experience of live music concerts.  This will provide an exemplar of how Annalist may be used as part of a larger ensemble of tools for creating and deploying applications using linked data.

We have noted that Annalist is not a "big data" system, and that design choices may constrain the effective size of a single Annalist collection.  But by creating multiple independent, cross-linked and web-searchable data, we anticipate that Annalist collections may be combined with other data sources, contributing to creation of linked data resources at larger scale.  One way to explore this idea would be to use Annalist to reinstate public access to the FlyTED data.  Some initial explorations are under way, and successful achievement of this could provide a particularly compelling evaluation of the Annalist principles and design.

<!--
    Notes:
    1. content: data bridges
    2. back end: LDP/SoLiD
    3. access: improved overview presentation and navigation
    4. sustainability: promote creation of a community of users and developers
-->

Looking ahead, we anticipate creation of "data bridges" to allow existing data (especially in spreadsheets) to be presented as linked data through Annalist; this might extend further to real-time data acquisition, with data from sensors like GPS or real-time feeds.

The current implementation of Annalist uses the server host file system for data storage, but it was an original goal that Annalist could work with third-party storage. A candidate for this would be a Linked Data Platform (LDP)\cite{w3c-ldp} server, though there are matters of access control to be resolved. The Social Linked Data (Solid) project\footnote{\url{https://github.com/solid/solid-spec}} uses WebId\footnote{\url{http://www.w3.org/2005/Incubator/webid/spec/identity/}} for access control, and could provide an promising opportunity if it is possible to devise a mechanism to link OpenID Connect authentication with WebId authorization.

Other areas of possible future work for Annalist include provenance\cite{w3c-prov-overview} recording and support for provenance ping-backs\cite{w3c-prov-aq} to recognize downstream use of Annalist data.

Looking further ahead, we note that the Annalist dynamic form generator has evolved in a somewhat ad hoc fashion, in response to evolving recognition of requirements. As noted in section \ref{data-sharing-platforms}, theoretical work on "form lenses"\cite{rajkumar2013} might be adopted to provide a more principled grounding for this aspect of Annalist.

Finally, we note that while Annalist has been an open development from its outset, it has been significantly conducted so far by an "open community" of just one developer. For a viable future we must engage a wider community of users and developers to establish a more long-term sustainable project.  Contributions will be most welcome!

# Conclusions

Annalist has been used in a number of research projects for prototyping linked data information structures and, even as a work-in-progress, has proven flexible and robust in use by a small number of diverse users, with a low cost to get started with a new collection. It has also proved effective in personal information management projects involving annotation of existing web resources and sharing structured data on the Web. While many of the capabilities of Annalist are provided by other systems, we are not aware of any other that combines the key features of Annalist in a package that can be used "out of the box" for data management.

We have noticed that, while Annalist is easy to use for basic data entry and browsing, developing more complex structures requires greater effort, and does benefit from an awareness of the RDF model (particularly with respect to the use of URIs, or CURIEs, to identify things, classes of things and relations between things). But this effort can be applied incrementally, yielding rapid benefits and feedback, supporting agility in creating information designs.

Annalist's flexible approach to information structuring has permitted an approach that differs from that often used when creating databases (e.g. for research data), starting with a very loosely structured narrative and progressively refining structured information around that narrative. In this, we feel that we have created a tool that goes some way to achieving Karger's objectives for semantic web applications, *viz.* "to work effectively over whatever schemas their users choose to create or import"\cite{karger2013b}.


# Acknowledgements

The development and evaluation of Annalist has been supported in part by 
EPSRC EP/L019981/1 Fusing Semantic and Audio Technologies for Intelligent Music Production and Consumption 
and by the JISC-funded Research Data Spring CREAM project\footnote{\url{https://blog.soton.ac.uk/cream/}}.

<!--  
##  Other links or systems (not mentioned)

  http://www.w3.org/2001/sw/wiki/Category:Editor (Need to check through: many tools are ontology editors or graph-based RDF editors)
  
  http://2014.eswc-conferences.org/sites/default/files/eswc2014pd_submission_46.pdf (example software paper to LODW
 
    https://github.com/zepheira/bibframe-scribe http://www.loc.gov/bibframe/ (feels more like a specialised bibliography tool - "Initiated by the Library of Congress, BIBFRAME provides a foundation for the future of bibliographic description, both on the web, and in the broader networked world.")
 
  http://www.linkeddatatools.com/rdf-studio
  
  Hypercard
  
  http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.97.950&rep=rep1&type=pdf (Tabulator, 2006)
  
  http://www.cognitum.eu/Semantics/FluentEditor/ (ontology editor using controlled natural language)

  http://ceur-ws.org/Vol-1184/ (LDoW 2014)
  
  http://ceur-ws.org/Vol-1184/ldow2014_paper_04.pdf
  
  http://ceur-ws.org/Vol-1184/ldow2014_paper_02.pdf (cf further work?)
  
  http://ceur-ws.org/Vol-1184/ldow2014_paper_06.pdf (LDOW software paper)
  
  http://haystack.csail.mit.edu/blog/2012/02/17/personal-information-management-is-not-personal-information-management/ (esp spreadsheets)
  
  https://wiki.duraspace.org/pages/viewpage.action?pageId=69014248
  
  http://hdlab.stanford.edu/lab-notebook/piranesi/2014/08/20/idiographic-diagramming-plus-linked-data/
 -->

    