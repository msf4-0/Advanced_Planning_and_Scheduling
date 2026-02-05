--
-- PostgreSQL database dump
--

\restrict bAGdEkhW4TcjUQN8YLRlCLHaB8CgXoZuk1qfdXFqRioUwG50CeAjuabi3x3Zg4s

-- Dumped from database version 15.15 (Debian 15.15-1.pgdg13+1)
-- Dumped by pg_dump version 15.15 (Debian 15.15-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: ag_catalog; Type: SCHEMA; Schema: -; Owner: postgresUser
--

CREATE SCHEMA ag_catalog;


ALTER SCHEMA ag_catalog OWNER TO "postgresUser";

--
-- Name: production_graph; Type: SCHEMA; Schema: -; Owner: postgresUser
--

CREATE SCHEMA production_graph;


ALTER SCHEMA production_graph OWNER TO "postgresUser";

--
-- Name: age; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS age WITH SCHEMA ag_catalog;


--
-- Name: EXTENSION age; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION age IS 'AGE database extension';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: _ag_label_edge; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph._ag_label_edge (
    id ag_catalog.graphid NOT NULL,
    start_id ag_catalog.graphid NOT NULL,
    end_id ag_catalog.graphid NOT NULL,
    properties ag_catalog.agtype DEFAULT ag_catalog.agtype_build_map() NOT NULL
);


ALTER TABLE production_graph._ag_label_edge OWNER TO "postgresUser";

--
-- Name: ALLOWED_ON; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph."ALLOWED_ON" (
)
INHERITS (production_graph._ag_label_edge);


ALTER TABLE production_graph."ALLOWED_ON" OWNER TO "postgresUser";

--
-- Name: ALLOWED_ON_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph."ALLOWED_ON_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER TABLE production_graph."ALLOWED_ON_id_seq" OWNER TO "postgresUser";

--
-- Name: ALLOWED_ON_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph."ALLOWED_ON_id_seq" OWNED BY production_graph."ALLOWED_ON".id;


--
-- Name: CAN_RUN_ON; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph."CAN_RUN_ON" (
)
INHERITS (production_graph._ag_label_edge);


ALTER TABLE production_graph."CAN_RUN_ON" OWNER TO "postgresUser";

--
-- Name: CAN_RUN_ON_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph."CAN_RUN_ON_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER TABLE production_graph."CAN_RUN_ON_id_seq" OWNER TO "postgresUser";

--
-- Name: CAN_RUN_ON_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph."CAN_RUN_ON_id_seq" OWNED BY production_graph."CAN_RUN_ON".id;


--
-- Name: _ag_label_vertex; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph._ag_label_vertex (
    id ag_catalog.graphid NOT NULL,
    properties ag_catalog.agtype DEFAULT ag_catalog.agtype_build_map() NOT NULL
);


ALTER TABLE production_graph._ag_label_vertex OWNER TO "postgresUser";

--
-- Name: Job; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph."Job" (
)
INHERITS (production_graph._ag_label_vertex);


ALTER TABLE production_graph."Job" OWNER TO "postgresUser";

--
-- Name: Job_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph."Job_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER TABLE production_graph."Job_id_seq" OWNER TO "postgresUser";

--
-- Name: Job_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph."Job_id_seq" OWNED BY production_graph."Job".id;


--
-- Name: Machine; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph."Machine" (
)
INHERITS (production_graph._ag_label_vertex);


ALTER TABLE production_graph."Machine" OWNER TO "postgresUser";

--
-- Name: Machine_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph."Machine_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER TABLE production_graph."Machine_id_seq" OWNER TO "postgresUser";

--
-- Name: Machine_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph."Machine_id_seq" OWNED BY production_graph."Machine".id;


--
-- Name: Material; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph."Material" (
)
INHERITS (production_graph._ag_label_vertex);


ALTER TABLE production_graph."Material" OWNER TO "postgresUser";

--
-- Name: Material_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph."Material_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER TABLE production_graph."Material_id_seq" OWNER TO "postgresUser";

--
-- Name: Material_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph."Material_id_seq" OWNED BY production_graph."Material".id;


--
-- Name: PRECEDES; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph."PRECEDES" (
)
INHERITS (production_graph._ag_label_edge);


ALTER TABLE production_graph."PRECEDES" OWNER TO "postgresUser";

--
-- Name: PRECEDES_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph."PRECEDES_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER TABLE production_graph."PRECEDES_id_seq" OWNER TO "postgresUser";

--
-- Name: PRECEDES_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph."PRECEDES_id_seq" OWNED BY production_graph."PRECEDES".id;


--
-- Name: _ag_label_edge_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph._ag_label_edge_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER TABLE production_graph._ag_label_edge_id_seq OWNER TO "postgresUser";

--
-- Name: _ag_label_edge_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph._ag_label_edge_id_seq OWNED BY production_graph._ag_label_edge.id;


--
-- Name: _ag_label_vertex_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph._ag_label_vertex_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER TABLE production_graph._ag_label_vertex_id_seq OWNER TO "postgresUser";

--
-- Name: _ag_label_vertex_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph._ag_label_vertex_id_seq OWNED BY production_graph._ag_label_vertex.id;


--
-- Name: _label_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph._label_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 65535
    CACHE 1
    CYCLE;


ALTER TABLE production_graph._label_id_seq OWNER TO "postgresUser";

--
-- Name: jobs; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.jobs (
    job_id text NOT NULL,
    duration integer,
    domain_start integer,
    domain_end integer,
    predecessor text,
    due_date integer,
    qty_ordered integer,
    qty_initialized integer,
    locked boolean,
    locked_start integer,
    locked_machine integer,
    required_machine_type_id integer
);


ALTER TABLE public.jobs OWNER TO "postgresUser";

--
-- Name: machine_types; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.machine_types (
    type_id integer NOT NULL,
    type_name text NOT NULL
);


ALTER TABLE public.machine_types OWNER TO "postgresUser";

--
-- Name: machine_types_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgresUser
--

CREATE SEQUENCE public.machine_types_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.machine_types_type_id_seq OWNER TO "postgresUser";

--
-- Name: machine_types_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgresUser
--

ALTER SEQUENCE public.machine_types_type_id_seq OWNED BY public.machine_types.type_id;


--
-- Name: machines; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.machines (
    machine_id integer NOT NULL,
    type text,
    capacity integer,
    machine_type_id integer
);


ALTER TABLE public.machines OWNER TO "postgresUser";

--
-- Name: materials; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.materials (
    material_id text NOT NULL,
    material_name text
);


ALTER TABLE public.materials OWNER TO "postgresUser";

--
-- Name: new_table; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.new_table (
    id integer NOT NULL,
    game character varying(255)
);


ALTER TABLE public.new_table OWNER TO "postgresUser";

--
-- Name: new_table_id_seq; Type: SEQUENCE; Schema: public; Owner: postgresUser
--

CREATE SEQUENCE public.new_table_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.new_table_id_seq OWNER TO "postgresUser";

--
-- Name: new_table_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgresUser
--

ALTER SEQUENCE public.new_table_id_seq OWNED BY public.new_table.id;


--
-- Name: testing; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.testing (
    id integer NOT NULL,
    name character varying(255) DEFAULT 'hi'::character varying NOT NULL,
    type integer NOT NULL
);


ALTER TABLE public.testing OWNER TO "postgresUser";

--
-- Name: testing2; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.testing2 (
    somn character varying(255),
    asdf character varying(255) NOT NULL
);


ALTER TABLE public.testing2 OWNER TO "postgresUser";

--
-- Name: testing_id_seq; Type: SEQUENCE; Schema: public; Owner: postgresUser
--

ALTER TABLE public.testing ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.testing_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: ALLOWED_ON id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."ALLOWED_ON" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'ALLOWED_ON'::name))::integer, nextval('production_graph."ALLOWED_ON_id_seq"'::regclass));


--
-- Name: ALLOWED_ON properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."ALLOWED_ON" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: CAN_RUN_ON id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."CAN_RUN_ON" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'CAN_RUN_ON'::name))::integer, nextval('production_graph."CAN_RUN_ON_id_seq"'::regclass));


--
-- Name: CAN_RUN_ON properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."CAN_RUN_ON" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: Job id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."Job" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'Job'::name))::integer, nextval('production_graph."Job_id_seq"'::regclass));


--
-- Name: Job properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."Job" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: Machine id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."Machine" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'Machine'::name))::integer, nextval('production_graph."Machine_id_seq"'::regclass));


--
-- Name: Machine properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."Machine" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: Material id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."Material" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'Material'::name))::integer, nextval('production_graph."Material_id_seq"'::regclass));


--
-- Name: Material properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."Material" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: PRECEDES id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."PRECEDES" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'PRECEDES'::name))::integer, nextval('production_graph."PRECEDES_id_seq"'::regclass));


--
-- Name: PRECEDES properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."PRECEDES" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: _ag_label_edge id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph._ag_label_edge ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, '_ag_label_edge'::name))::integer, nextval('production_graph._ag_label_edge_id_seq'::regclass));


--
-- Name: _ag_label_vertex id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph._ag_label_vertex ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, '_ag_label_vertex'::name))::integer, nextval('production_graph._ag_label_vertex_id_seq'::regclass));


--
-- Name: machine_types type_id; Type: DEFAULT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.machine_types ALTER COLUMN type_id SET DEFAULT nextval('public.machine_types_type_id_seq'::regclass);


--
-- Name: new_table id; Type: DEFAULT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.new_table ALTER COLUMN id SET DEFAULT nextval('public.new_table_id_seq'::regclass);


--
-- Data for Name: ag_graph; Type: TABLE DATA; Schema: ag_catalog; Owner: postgresUser
--

COPY ag_catalog.ag_graph (graphid, name, namespace) FROM stdin;
17056	production_graph	production_graph
\.


--
-- Data for Name: ag_label; Type: TABLE DATA; Schema: ag_catalog; Owner: postgresUser
--

COPY ag_catalog.ag_label (name, graph, id, kind, relation, seq_name) FROM stdin;
_ag_label_vertex	17056	1	v	production_graph._ag_label_vertex	_ag_label_vertex_id_seq
_ag_label_edge	17056	2	e	production_graph._ag_label_edge	_ag_label_edge_id_seq
Machine	17056	3	v	production_graph."Machine"	Machine_id_seq
Job	17056	4	v	production_graph."Job"	Job_id_seq
Material	17056	5	v	production_graph."Material"	Material_id_seq
CAN_RUN_ON	17056	6	e	production_graph."CAN_RUN_ON"	CAN_RUN_ON_id_seq
PRECEDES	17056	7	e	production_graph."PRECEDES"	PRECEDES_id_seq
ALLOWED_ON	17056	8	e	production_graph."ALLOWED_ON"	ALLOWED_ON_id_seq
\.


--
-- Data for Name: ALLOWED_ON; Type: TABLE DATA; Schema: production_graph; Owner: postgresUser
--

COPY production_graph."ALLOWED_ON" (id, start_id, end_id, properties) FROM stdin;
2251799813685249	1125899906842625	844424930131969	{}
2251799813685250	1125899906842625	844424930131970	{}
2251799813685251	1125899906842626	844424930131970	{}
2251799813685252	1125899906842627	844424930131969	{}
2251799813685253	1125899906842628	844424930131970	{}
2251799813685254	1125899906842628	844424930131971	{}
2251799813685255	1125899906842629	844424930131971	{}
\.


--
-- Data for Name: CAN_RUN_ON; Type: TABLE DATA; Schema: production_graph; Owner: postgresUser
--

COPY production_graph."CAN_RUN_ON" (id, start_id, end_id, properties) FROM stdin;
1688849860263937	1125899906842625	844424930131969	{}
1688849860263938	1125899906842625	844424930131970	{}
1688849860263939	1125899906842626	844424930131970	{}
1688849860263940	1125899906842627	844424930131969	{}
1688849860263941	1125899906842628	844424930131970	{}
1688849860263942	1125899906842628	844424930131971	{}
1688849860263943	1125899906842629	844424930131971	{}
\.


--
-- Data for Name: Job; Type: TABLE DATA; Schema: production_graph; Owner: postgresUser
--

COPY production_graph."Job" (id, properties) FROM stdin;
1125899906842625	{"job_id": "jobA", "locked": false, "due_date": 15, "duration": 5, "domain_end": 20, "qty_ordered": 100, "domain_start": 0, "qty_initialized": 90}
1125899906842626	{"job_id": "jobB", "locked": false, "due_date": 20, "duration": 7, "domain_end": 25, "predecessor": "jobA", "qty_ordered": 120, "domain_start": 0, "qty_initialized": 110}
1125899906842627	{"job_id": "jobC", "locked": true, "due_date": 10, "duration": 4, "domain_end": 18, "qty_ordered": 80, "domain_start": 0, "locked_start": 2, "locked_machine": 1, "qty_initialized": 80}
1125899906842628	{"job_id": "jobD", "locked": false, "due_date": 15, "duration": 10, "domain_end": 20, "qty_ordered": 100, "domain_start": 0, "qty_initialized": 90}
1125899906842629	{"job_id": "jobE", "locked": false, "due_date": 15, "duration": 15, "domain_end": 20, "qty_ordered": 100, "domain_start": 0, "qty_initialized": 90}
\.


--
-- Data for Name: Machine; Type: TABLE DATA; Schema: production_graph; Owner: postgresUser
--

COPY production_graph."Machine" (id, properties) FROM stdin;
844424930131969	{"type": "CNC", "capacity": 2, "machine_id": 1}
844424930131970	{"type": "Lathe", "capacity": 1, "machine_id": 2}
844424930131971	{"type": "Milling", "capacity": 1, "machine_id": 3}
\.


--
-- Data for Name: Material; Type: TABLE DATA; Schema: production_graph; Owner: postgresUser
--

COPY production_graph."Material" (id, properties) FROM stdin;
1407374883553281	{"material_id": "matA", "material_name": "Steel"}
1407374883553282	{"material_id": "matB", "material_name": "Aluminum"}
\.


--
-- Data for Name: PRECEDES; Type: TABLE DATA; Schema: production_graph; Owner: postgresUser
--

COPY production_graph."PRECEDES" (id, start_id, end_id, properties) FROM stdin;
1970324836974593	1125899906842626	1125899906842625	{}
1970324836974594	1125899906842625	1125899906842626	{}
\.


--
-- Data for Name: _ag_label_edge; Type: TABLE DATA; Schema: production_graph; Owner: postgresUser
--

COPY production_graph._ag_label_edge (id, start_id, end_id, properties) FROM stdin;
\.


--
-- Data for Name: _ag_label_vertex; Type: TABLE DATA; Schema: production_graph; Owner: postgresUser
--

COPY production_graph._ag_label_vertex (id, properties) FROM stdin;
\.


--
-- Data for Name: jobs; Type: TABLE DATA; Schema: public; Owner: postgresUser
--

COPY public.jobs (job_id, duration, domain_start, domain_end, predecessor, due_date, qty_ordered, qty_initialized, locked, locked_start, locked_machine, required_machine_type_id) FROM stdin;
jobE	15	0	20	\N	15	100	90	f	\N	\N	3
jobB	7	0	25	jobA	20	120	110	f	\N	\N	5
jobD	10	0	20	\N	15	100	90	f	\N	\N	5
jobC	4	0	18	\N	10	80	80	t	2	1	3
something	5	0	50	jobF	30	100	90	f	\N	\N	3
jobF	6	0	15	jobC	20	100	90	f	\N	\N	4
jobA	10	0	20	\N	15	100	90	f	\N	\N	3
newJob	2	10	13	jobA	15	50	50	f	\N	\N	4
paintingJob	5	5	20	\N	15	100	90	f	\N	\N	6
\.


--
-- Data for Name: machine_types; Type: TABLE DATA; Schema: public; Owner: postgresUser
--

COPY public.machine_types (type_id, type_name) FROM stdin;
3	CNC
4	Sawing
5	Milling
6	Painting
\.


--
-- Data for Name: machines; Type: TABLE DATA; Schema: public; Owner: postgresUser
--

COPY public.machines (machine_id, type, capacity, machine_type_id) FROM stdin;
1	CNC	2	3
2	Lathe	1	3
3	Milling	1	5
4	Sawing	2	4
5	Sawing	2	4
6	Painter	3	6
\.


--
-- Data for Name: materials; Type: TABLE DATA; Schema: public; Owner: postgresUser
--

COPY public.materials (material_id, material_name) FROM stdin;
matA	Steel
matB	Aluminum
\.


--
-- Data for Name: new_table; Type: TABLE DATA; Schema: public; Owner: postgresUser
--

COPY public.new_table (id, game) FROM stdin;
1	Elden Ring
\.


--
-- Data for Name: testing; Type: TABLE DATA; Schema: public; Owner: postgresUser
--

COPY public.testing (id, name, type) FROM stdin;
1	Alice	101
2	Bob	102
3	Charlie	103
4	Danielle	104
5	Bon	105
6	John	106
\.


--
-- Data for Name: testing2; Type: TABLE DATA; Schema: public; Owner: postgresUser
--

COPY public.testing2 (somn, asdf) FROM stdin;
apple	red
banana	yellow
carrot	orange
cucumber	green
someFruit	someColor
\.


--
-- Name: ALLOWED_ON_id_seq; Type: SEQUENCE SET; Schema: production_graph; Owner: postgresUser
--

SELECT pg_catalog.setval('production_graph."ALLOWED_ON_id_seq"', 7, true);


--
-- Name: CAN_RUN_ON_id_seq; Type: SEQUENCE SET; Schema: production_graph; Owner: postgresUser
--

SELECT pg_catalog.setval('production_graph."CAN_RUN_ON_id_seq"', 7, true);


--
-- Name: Job_id_seq; Type: SEQUENCE SET; Schema: production_graph; Owner: postgresUser
--

SELECT pg_catalog.setval('production_graph."Job_id_seq"', 5, true);


--
-- Name: Machine_id_seq; Type: SEQUENCE SET; Schema: production_graph; Owner: postgresUser
--

SELECT pg_catalog.setval('production_graph."Machine_id_seq"', 3, true);


--
-- Name: Material_id_seq; Type: SEQUENCE SET; Schema: production_graph; Owner: postgresUser
--

SELECT pg_catalog.setval('production_graph."Material_id_seq"', 2, true);


--
-- Name: PRECEDES_id_seq; Type: SEQUENCE SET; Schema: production_graph; Owner: postgresUser
--

SELECT pg_catalog.setval('production_graph."PRECEDES_id_seq"', 2, true);


--
-- Name: _ag_label_edge_id_seq; Type: SEQUENCE SET; Schema: production_graph; Owner: postgresUser
--

SELECT pg_catalog.setval('production_graph._ag_label_edge_id_seq', 1, false);


--
-- Name: _ag_label_vertex_id_seq; Type: SEQUENCE SET; Schema: production_graph; Owner: postgresUser
--

SELECT pg_catalog.setval('production_graph._ag_label_vertex_id_seq', 1, false);


--
-- Name: _label_id_seq; Type: SEQUENCE SET; Schema: production_graph; Owner: postgresUser
--

SELECT pg_catalog.setval('production_graph._label_id_seq', 8, true);


--
-- Name: machine_types_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgresUser
--

SELECT pg_catalog.setval('public.machine_types_type_id_seq', 6, true);


--
-- Name: new_table_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgresUser
--

SELECT pg_catalog.setval('public.new_table_id_seq', 1, true);


--
-- Name: testing_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgresUser
--

SELECT pg_catalog.setval('public.testing_id_seq', 6, true);


--
-- Name: _ag_label_edge _ag_label_edge_pkey; Type: CONSTRAINT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph._ag_label_edge
    ADD CONSTRAINT _ag_label_edge_pkey PRIMARY KEY (id);


--
-- Name: _ag_label_vertex _ag_label_vertex_pkey; Type: CONSTRAINT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph._ag_label_vertex
    ADD CONSTRAINT _ag_label_vertex_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (job_id);


--
-- Name: machine_types machine_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.machine_types
    ADD CONSTRAINT machine_types_pkey PRIMARY KEY (type_id);


--
-- Name: machine_types machine_types_type_name_key; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.machine_types
    ADD CONSTRAINT machine_types_type_name_key UNIQUE (type_name);


--
-- Name: machines machines_pkey; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.machines
    ADD CONSTRAINT machines_pkey PRIMARY KEY (machine_id);


--
-- Name: materials materials_pkey; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_pkey PRIMARY KEY (material_id);


--
-- Name: testing testing_pkey; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.testing
    ADD CONSTRAINT testing_pkey PRIMARY KEY (id);


--
-- Name: testing testing_type_key; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.testing
    ADD CONSTRAINT testing_type_key UNIQUE (type);


--
-- Name: jobs jobs_required_machine_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_required_machine_type_id_fkey FOREIGN KEY (required_machine_type_id) REFERENCES public.machine_types(type_id);


--
-- Name: machines machines_machine_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.machines
    ADD CONSTRAINT machines_machine_type_id_fkey FOREIGN KEY (machine_type_id) REFERENCES public.machine_types(type_id);


--
-- PostgreSQL database dump complete
--

\unrestrict bAGdEkhW4TcjUQN8YLRlCLHaB8CgXoZuk1qfdXFqRioUwG50CeAjuabi3x3Zg4s

