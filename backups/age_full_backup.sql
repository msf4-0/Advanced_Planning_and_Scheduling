--
-- PostgreSQL database dump
--

\restrict MwymxzVIFZ3YrUxnJv50HYG4qUw09tV9yDdhSgdbiYBQ86jA5mzEg7MU7ksVfcU

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
-- Name: ag_catalog; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA ag_catalog;


--
-- Name: production_graph; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA production_graph;


--
-- Name: age; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS age WITH SCHEMA ag_catalog;


--
-- Name: EXTENSION age; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION age IS 'AGE database extension';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: _ag_label_edge; Type: TABLE; Schema: production_graph; Owner: -
--

CREATE TABLE production_graph._ag_label_edge (
    id ag_catalog.graphid NOT NULL,
    start_id ag_catalog.graphid NOT NULL,
    end_id ag_catalog.graphid NOT NULL,
    properties ag_catalog.agtype DEFAULT ag_catalog.agtype_build_map() NOT NULL
);


--
-- Name: ALLOWED_ON; Type: TABLE; Schema: production_graph; Owner: -
--

CREATE TABLE production_graph."ALLOWED_ON" (
)
INHERITS (production_graph._ag_label_edge);


--
-- Name: ALLOWED_ON_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: -
--

CREATE SEQUENCE production_graph."ALLOWED_ON_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


--
-- Name: ALLOWED_ON_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: -
--

ALTER SEQUENCE production_graph."ALLOWED_ON_id_seq" OWNED BY production_graph."ALLOWED_ON".id;


--
-- Name: CAN_RUN_ON; Type: TABLE; Schema: production_graph; Owner: -
--

CREATE TABLE production_graph."CAN_RUN_ON" (
)
INHERITS (production_graph._ag_label_edge);


--
-- Name: CAN_RUN_ON_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: -
--

CREATE SEQUENCE production_graph."CAN_RUN_ON_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


--
-- Name: CAN_RUN_ON_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: -
--

ALTER SEQUENCE production_graph."CAN_RUN_ON_id_seq" OWNED BY production_graph."CAN_RUN_ON".id;


--
-- Name: _ag_label_vertex; Type: TABLE; Schema: production_graph; Owner: -
--

CREATE TABLE production_graph._ag_label_vertex (
    id ag_catalog.graphid NOT NULL,
    properties ag_catalog.agtype DEFAULT ag_catalog.agtype_build_map() NOT NULL
);


--
-- Name: Job; Type: TABLE; Schema: production_graph; Owner: -
--

CREATE TABLE production_graph."Job" (
)
INHERITS (production_graph._ag_label_vertex);


--
-- Name: Job_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: -
--

CREATE SEQUENCE production_graph."Job_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


--
-- Name: Job_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: -
--

ALTER SEQUENCE production_graph."Job_id_seq" OWNED BY production_graph."Job".id;


--
-- Name: Machine; Type: TABLE; Schema: production_graph; Owner: -
--

CREATE TABLE production_graph."Machine" (
)
INHERITS (production_graph._ag_label_vertex);


--
-- Name: Machine_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: -
--

CREATE SEQUENCE production_graph."Machine_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


--
-- Name: Machine_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: -
--

ALTER SEQUENCE production_graph."Machine_id_seq" OWNED BY production_graph."Machine".id;


--
-- Name: Material; Type: TABLE; Schema: production_graph; Owner: -
--

CREATE TABLE production_graph."Material" (
)
INHERITS (production_graph._ag_label_vertex);


--
-- Name: Material_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: -
--

CREATE SEQUENCE production_graph."Material_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


--
-- Name: Material_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: -
--

ALTER SEQUENCE production_graph."Material_id_seq" OWNED BY production_graph."Material".id;


--
-- Name: PRECEDES; Type: TABLE; Schema: production_graph; Owner: -
--

CREATE TABLE production_graph."PRECEDES" (
)
INHERITS (production_graph._ag_label_edge);


--
-- Name: PRECEDES_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: -
--

CREATE SEQUENCE production_graph."PRECEDES_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


--
-- Name: PRECEDES_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: -
--

ALTER SEQUENCE production_graph."PRECEDES_id_seq" OWNED BY production_graph."PRECEDES".id;


--
-- Name: _ag_label_edge_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: -
--

CREATE SEQUENCE production_graph._ag_label_edge_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


--
-- Name: _ag_label_edge_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: -
--

ALTER SEQUENCE production_graph._ag_label_edge_id_seq OWNED BY production_graph._ag_label_edge.id;


--
-- Name: _ag_label_vertex_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: -
--

CREATE SEQUENCE production_graph._ag_label_vertex_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


--
-- Name: _ag_label_vertex_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: -
--

ALTER SEQUENCE production_graph._ag_label_vertex_id_seq OWNED BY production_graph._ag_label_vertex.id;


--
-- Name: _label_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: -
--

CREATE SEQUENCE production_graph._label_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 65535
    CACHE 1
    CYCLE;


--
-- Name: config; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.config (
    key text NOT NULL,
    value text
);


--
-- Name: jobs; Type: TABLE; Schema: public; Owner: -
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


--
-- Name: machine_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.machine_types (
    type_id integer NOT NULL,
    type_name text NOT NULL
);


--
-- Name: machine_types_type_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.machine_types_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: machine_types_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.machine_types_type_id_seq OWNED BY public.machine_types.type_id;


--
-- Name: machines; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.machines (
    machine_id integer NOT NULL,
    type text,
    capacity integer,
    machine_type_id integer
);


--
-- Name: materials; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.materials (
    material_id text NOT NULL,
    material_name text
);


--
-- Name: schedule_result; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schedule_result (
    id integer NOT NULL,
    result jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: schedule_result_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.schedule_result_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: schedule_result_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.schedule_result_id_seq OWNED BY public.schedule_result.id;


--
-- Name: ALLOWED_ON id; Type: DEFAULT; Schema: production_graph; Owner: -
--

ALTER TABLE ONLY production_graph."ALLOWED_ON" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'ALLOWED_ON'::name))::integer, nextval('production_graph."ALLOWED_ON_id_seq"'::regclass));


--
-- Name: ALLOWED_ON properties; Type: DEFAULT; Schema: production_graph; Owner: -
--

ALTER TABLE ONLY production_graph."ALLOWED_ON" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: CAN_RUN_ON id; Type: DEFAULT; Schema: production_graph; Owner: -
--

ALTER TABLE ONLY production_graph."CAN_RUN_ON" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'CAN_RUN_ON'::name))::integer, nextval('production_graph."CAN_RUN_ON_id_seq"'::regclass));


--
-- Name: CAN_RUN_ON properties; Type: DEFAULT; Schema: production_graph; Owner: -
--

ALTER TABLE ONLY production_graph."CAN_RUN_ON" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: Job id; Type: DEFAULT; Schema: production_graph; Owner: -
--

ALTER TABLE ONLY production_graph."Job" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'Job'::name))::integer, nextval('production_graph."Job_id_seq"'::regclass));


--
-- Name: Job properties; Type: DEFAULT; Schema: production_graph; Owner: -
--

ALTER TABLE ONLY production_graph."Job" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: Machine id; Type: DEFAULT; Schema: production_graph; Owner: -
--

ALTER TABLE ONLY production_graph."Machine" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'Machine'::name))::integer, nextval('production_graph."Machine_id_seq"'::regclass));


--
-- Name: Machine properties; Type: DEFAULT; Schema: production_graph; Owner: -
--

ALTER TABLE ONLY production_graph."Machine" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: Material id; Type: DEFAULT; Schema: production_graph; Owner: -
--

ALTER TABLE ONLY production_graph."Material" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'Material'::name))::integer, nextval('production_graph."Material_id_seq"'::regclass));


--
-- Name: Material properties; Type: DEFAULT; Schema: production_graph; Owner: -
--

ALTER TABLE ONLY production_graph."Material" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: PRECEDES id; Type: DEFAULT; Schema: production_graph; Owner: -
--

ALTER TABLE ONLY production_graph."PRECEDES" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'PRECEDES'::name))::integer, nextval('production_graph."PRECEDES_id_seq"'::regclass));


--
-- Name: PRECEDES properties; Type: DEFAULT; Schema: production_graph; Owner: -
--

ALTER TABLE ONLY production_graph."PRECEDES" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: _ag_label_edge id; Type: DEFAULT; Schema: production_graph; Owner: -
--

ALTER TABLE ONLY production_graph._ag_label_edge ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, '_ag_label_edge'::name))::integer, nextval('production_graph._ag_label_edge_id_seq'::regclass));


--
-- Name: _ag_label_vertex id; Type: DEFAULT; Schema: production_graph; Owner: -
--

ALTER TABLE ONLY production_graph._ag_label_vertex ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, '_ag_label_vertex'::name))::integer, nextval('production_graph._ag_label_vertex_id_seq'::regclass));


--
-- Name: machine_types type_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.machine_types ALTER COLUMN type_id SET DEFAULT nextval('public.machine_types_type_id_seq'::regclass);


--
-- Name: schedule_result id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_result ALTER COLUMN id SET DEFAULT nextval('public.schedule_result_id_seq'::regclass);


--
-- Data for Name: ag_graph; Type: TABLE DATA; Schema: ag_catalog; Owner: -
--

COPY ag_catalog.ag_graph (graphid, name, namespace) FROM stdin;
17056	production_graph	production_graph
\.


--
-- Data for Name: ag_label; Type: TABLE DATA; Schema: ag_catalog; Owner: -
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
-- Data for Name: ALLOWED_ON; Type: TABLE DATA; Schema: production_graph; Owner: -
--

COPY production_graph."ALLOWED_ON" (id, start_id, end_id, properties) FROM stdin;
2251799813685249	1125899906842625	844424930131969	{}
2251799813685250	1125899906842625	844424930131970	{}
2251799813685251	1125899906842626	844424930131970	{}
2251799813685252	1125899906842627	844424930131969	{}
2251799813685253	1125899906842628	844424930131970	{}
2251799813685254	1125899906842628	844424930131971	{}
2251799813685255	1125899906842629	844424930131971	{}
2251799813685249	1125899906842625	844424930131969	{}
2251799813685250	1125899906842625	844424930131970	{}
2251799813685251	1125899906842626	844424930131970	{}
2251799813685252	1125899906842627	844424930131969	{}
2251799813685253	1125899906842628	844424930131970	{}
2251799813685254	1125899906842628	844424930131971	{}
2251799813685255	1125899906842629	844424930131971	{}
\.


--
-- Data for Name: CAN_RUN_ON; Type: TABLE DATA; Schema: production_graph; Owner: -
--

COPY production_graph."CAN_RUN_ON" (id, start_id, end_id, properties) FROM stdin;
1688849860263937	1125899906842625	844424930131969	{}
1688849860263938	1125899906842625	844424930131970	{}
1688849860263939	1125899906842626	844424930131970	{}
1688849860263940	1125899906842627	844424930131969	{}
1688849860263941	1125899906842628	844424930131970	{}
1688849860263942	1125899906842628	844424930131971	{}
1688849860263943	1125899906842629	844424930131971	{}
1688849860263937	1125899906842625	844424930131969	{}
1688849860263938	1125899906842625	844424930131970	{}
1688849860263939	1125899906842626	844424930131970	{}
1688849860263940	1125899906842627	844424930131969	{}
1688849860263941	1125899906842628	844424930131970	{}
1688849860263942	1125899906842628	844424930131971	{}
1688849860263943	1125899906842629	844424930131971	{}
\.


--
-- Data for Name: Job; Type: TABLE DATA; Schema: production_graph; Owner: -
--

COPY production_graph."Job" (id, properties) FROM stdin;
1125899906842625	{"job_id": "jobA", "locked": false, "due_date": 15, "duration": 5, "domain_end": 20, "qty_ordered": 100, "domain_start": 0, "qty_initialized": 90}
1125899906842626	{"job_id": "jobB", "locked": false, "due_date": 20, "duration": 7, "domain_end": 25, "predecessor": "jobA", "qty_ordered": 120, "domain_start": 0, "qty_initialized": 110}
1125899906842627	{"job_id": "jobC", "locked": true, "due_date": 10, "duration": 4, "domain_end": 18, "qty_ordered": 80, "domain_start": 0, "locked_start": 2, "locked_machine": 1, "qty_initialized": 80}
1125899906842628	{"job_id": "jobD", "locked": false, "due_date": 15, "duration": 10, "domain_end": 20, "qty_ordered": 100, "domain_start": 0, "qty_initialized": 90}
1125899906842629	{"job_id": "jobE", "locked": false, "due_date": 15, "duration": 15, "domain_end": 20, "qty_ordered": 100, "domain_start": 0, "qty_initialized": 90}
1125899906842625	{"job_id": "jobA", "locked": false, "due_date": 15, "duration": 5, "domain_end": 20, "qty_ordered": 100, "domain_start": 0, "qty_initialized": 90}
1125899906842626	{"job_id": "jobB", "locked": false, "due_date": 20, "duration": 7, "domain_end": 25, "predecessor": "jobA", "qty_ordered": 120, "domain_start": 0, "qty_initialized": 110}
1125899906842627	{"job_id": "jobC", "locked": true, "due_date": 10, "duration": 4, "domain_end": 18, "qty_ordered": 80, "domain_start": 0, "locked_start": 2, "locked_machine": 1, "qty_initialized": 80}
1125899906842628	{"job_id": "jobD", "locked": false, "due_date": 15, "duration": 10, "domain_end": 20, "qty_ordered": 100, "domain_start": 0, "qty_initialized": 90}
1125899906842629	{"job_id": "jobE", "locked": false, "due_date": 15, "duration": 15, "domain_end": 20, "qty_ordered": 100, "domain_start": 0, "qty_initialized": 90}
\.


--
-- Data for Name: Machine; Type: TABLE DATA; Schema: production_graph; Owner: -
--

COPY production_graph."Machine" (id, properties) FROM stdin;
844424930131969	{"type": "CNC", "capacity": 2, "machine_id": 1}
844424930131970	{"type": "Lathe", "capacity": 1, "machine_id": 2}
844424930131971	{"type": "Milling", "capacity": 1, "machine_id": 3}
844424930131969	{"type": "CNC", "capacity": 2, "machine_id": 1}
844424930131970	{"type": "Lathe", "capacity": 1, "machine_id": 2}
844424930131971	{"type": "Milling", "capacity": 1, "machine_id": 3}
\.


--
-- Data for Name: Material; Type: TABLE DATA; Schema: production_graph; Owner: -
--

COPY production_graph."Material" (id, properties) FROM stdin;
1407374883553281	{"material_id": "matA", "material_name": "Steel"}
1407374883553282	{"material_id": "matB", "material_name": "Aluminum"}
1407374883553281	{"material_id": "matA", "material_name": "Steel"}
1407374883553282	{"material_id": "matB", "material_name": "Aluminum"}
\.


--
-- Data for Name: PRECEDES; Type: TABLE DATA; Schema: production_graph; Owner: -
--

COPY production_graph."PRECEDES" (id, start_id, end_id, properties) FROM stdin;
1970324836974593	1125899906842626	1125899906842625	{}
1970324836974594	1125899906842625	1125899906842626	{}
1970324836974593	1125899906842626	1125899906842625	{}
1970324836974594	1125899906842625	1125899906842626	{}
\.


--
-- Data for Name: _ag_label_edge; Type: TABLE DATA; Schema: production_graph; Owner: -
--

COPY production_graph._ag_label_edge (id, start_id, end_id, properties) FROM stdin;
\.


--
-- Data for Name: _ag_label_vertex; Type: TABLE DATA; Schema: production_graph; Owner: -
--

COPY production_graph._ag_label_vertex (id, properties) FROM stdin;
\.


--
-- Data for Name: config; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.config (key, value) FROM stdin;
toggle_autoRun	TRUE
job_tableName	jobs
\.


--
-- Data for Name: jobs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.jobs (job_id, duration, domain_start, domain_end, predecessor, due_date, qty_ordered, qty_initialized, locked, locked_start, locked_machine, required_machine_type_id) FROM stdin;
jobE	15	0	20	\N	15	100	90	f	\N	\N	3
jobB	7	0	25	jobA	20	120	110	f	\N	\N	5
jobD	10	0	20	\N	15	100	90	f	\N	\N	5
jobF	6	0	15	jobC	20	100	90	f	\N	\N	4
jobA	10	0	20	\N	15	100	90	f	\N	\N	3
paintingJob	5	5	20	\N	15	100	90	f	\N	\N	6
jobC	4	0	18	\N	10	80	80	t	2	1	7
Panting2	15	0	20	\N	15	100	90	f	\N	\N	3
Assembly Job	5	0	20	\N	15	100	90	f	\N	\N	4
Calculating	3	0	20	jobB	15	100	90	f	\N	\N	5
Programming Job	6	0	20	jobA	15	100	90	f	\N	\N	4
Wood	5	0	20	jobF	15	100	90	f	\N	\N	5
Production	10	0	20	\N	15	100	90	f	\N	\N	6
\.


--
-- Data for Name: machine_types; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.machine_types (type_id, type_name) FROM stdin;
3	CNC
4	Sawing
5	Milling
6	Painting
7	Assembly
\.


--
-- Data for Name: machines; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.machines (machine_id, type, capacity, machine_type_id) FROM stdin;
2	Lathe	1	3
3	Milling	1	5
4	Sawing	2	4
5	Sawing	2	4
6	Painter	3	6
7	Assembly	2	7
1	CNC	2	3
\.


--
-- Data for Name: materials; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.materials (material_id, material_name) FROM stdin;
matA	Steel
matB	Aluminum
\.


--
-- Data for Name: schedule_result; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.schedule_result (id, result, created_at) FROM stdin;
1	{"jobA": {"end": 10, "start": 0, "machine": 1}, "jobB": {"end": 17, "start": 10, "machine": 3}, "jobC": {"end": 6, "start": 2, "machine": 1}, "jobD": {"end": 10, "start": 0, "machine": 3}, "jobE": {"end": 15, "start": 0, "machine": 1}, "jobF": {"end": 12, "start": 6, "machine": 4}, "newJob": {"end": 12, "start": 10, "machine": 4}, "paintingJob": {"end": 5, "start": 0, "machine": 6}}	2026-02-12 01:15:36.792166
2	{"jobA": {"end": 10, "start": 0, "machine": 1}, "jobB": {"end": 17, "start": 10, "machine": 3}, "jobC": {"end": 6, "start": 2, "machine": 1}, "jobD": {"end": 10, "start": 0, "machine": 3}, "jobE": {"end": 15, "start": 0, "machine": 1}, "jobF": {"end": 12, "start": 6, "machine": 4}, "newJob": {"end": 12, "start": 10, "machine": 4}, "paintingJob": {"end": 5, "start": 0, "machine": 6}}	2026-02-12 01:15:40.546615
3	{"jobA": {"end": 10, "start": 0, "machine": 1}, "jobB": {"end": 17, "start": 10, "machine": 3}, "jobC": {"end": 6, "start": 2, "machine": 1}, "jobD": {"end": 10, "start": 0, "machine": 3}, "jobE": {"end": 15, "start": 0, "machine": 1}, "jobF": {"end": 12, "start": 6, "machine": 4}, "paintingJob": {"end": 5, "start": 0, "machine": 6}}	2026-02-12 01:16:04.60846
4	{"jobA": {"end": 10, "start": 0, "resources": 1}, "jobB": {"end": 17, "start": 10, "resources": 3}, "jobC": {"end": 6, "start": 2, "resources": 7}, "jobD": {"end": 10, "start": 0, "resources": 3}, "jobE": {"end": 25, "start": 10, "resources": 1}, "jobF": {"end": 12, "start": 6, "resources": 4}, "paintingJob": {"end": 5, "start": 0, "resources": 6}}	2026-02-12 02:53:43.759017
5	{"jobA": {"end": 10, "start": 0, "resources": 1}, "jobB": {"end": 17, "start": 10, "resources": 3}, "jobC": {"end": 6, "start": 2, "resources": 7}, "jobD": {"end": 10, "start": 0, "resources": 3}, "jobE": {"end": 25, "start": 10, "resources": 1}, "jobF": {"end": 12, "start": 6, "resources": 4}, "paintingJob": {"end": 5, "start": 0, "resources": 6}}	2026-02-12 02:54:35.434894
6	{"jobA": {"end": 10, "start": 0, "resources": 1}, "jobB": {"end": 17, "start": 10, "resources": 3}, "jobC": {"end": 6, "start": 2, "resources": 7}, "jobD": {"end": 10, "start": 0, "resources": 3}, "jobE": {"end": 25, "start": 10, "resources": 1}, "jobF": {"end": 12, "start": 6, "resources": 4}, "paintingJob": {"end": 5, "start": 0, "resources": 6}}	2026-02-12 03:26:34.133708
7	{"jobA": {"end": 10, "start": 0, "resources": 1}, "jobB": {"end": 17, "start": 10, "resources": 3}, "jobC": {"end": 6, "start": 2, "resources": 7}, "jobD": {"end": 10, "start": 0, "resources": 3}, "jobE": {"end": 40, "start": 25, "resources": 1}, "jobF": {"end": 12, "start": 6, "resources": 4}, "Panting2": {"end": 25, "start": 10, "resources": 1}, "paintingJob": {"end": 5, "start": 0, "resources": 6}}	2026-02-12 06:03:02.960432
8	{"jobA": {"end": 10, "start": 0, "resources": 1}, "jobB": {"end": 17, "start": 10, "resources": 3}, "jobC": {"end": 6, "start": 2, "resources": 7}, "jobD": {"end": 10, "start": 0, "resources": 3}, "jobE": {"end": 25, "start": 10, "resources": 1}, "jobF": {"end": 12, "start": 6, "resources": 4}, "Panting2": {"end": 40, "start": 25, "resources": 1}, "paintingJob": {"end": 5, "start": 0, "resources": 6}, "Assembly Job": {"end": 5, "start": 0, "resources": 4}}	2026-02-12 08:32:43.23018
9	{"jobA": {"end": 10, "start": 0, "resources": 1}, "jobB": {"end": 17, "start": 10, "resources": 3}, "jobC": {"end": 6, "start": 2, "resources": 7}, "jobD": {"end": 10, "start": 0, "resources": 3}, "jobE": {"end": 25, "start": 10, "resources": 1}, "jobF": {"end": 12, "start": 6, "resources": 4}, "Panting2": {"end": 40, "start": 25, "resources": 1}, "Calculating": {"end": 20, "start": 17, "resources": 3}, "paintingJob": {"end": 5, "start": 0, "resources": 6}, "Assembly Job": {"end": 5, "start": 0, "resources": 4}}	2026-02-12 08:43:35.247649
10	{"jobA": {"end": 10, "start": 0, "resources": 1}, "jobB": {"end": 17, "start": 10, "resources": 3}, "jobC": {"end": 6, "start": 2, "resources": 7}, "jobD": {"end": 10, "start": 0, "resources": 3}, "jobE": {"end": 25, "start": 10, "resources": 1}, "jobF": {"end": 12, "start": 6, "resources": 4}, "Panting2": {"end": 40, "start": 25, "resources": 1}, "Calculating": {"end": 20, "start": 17, "resources": 3}, "paintingJob": {"end": 5, "start": 0, "resources": 6}, "Assembly Job": {"end": 5, "start": 0, "resources": 4}, "Programming Job": {"end": 18, "start": 12, "resources": 4}}	2026-02-12 08:51:53.587379
11	{"Wood": {"end": 25, "start": 20, "resources": 3}, "jobA": {"end": 10, "start": 0, "resources": 1}, "jobB": {"end": 17, "start": 10, "resources": 3}, "jobC": {"end": 6, "start": 2, "resources": 7}, "jobD": {"end": 10, "start": 0, "resources": 3}, "jobE": {"end": 40, "start": 25, "resources": 1}, "jobF": {"end": 12, "start": 6, "resources": 4}, "Panting2": {"end": 25, "start": 10, "resources": 1}, "Calculating": {"end": 20, "start": 17, "resources": 3}, "paintingJob": {"end": 5, "start": 0, "resources": 6}, "Assembly Job": {"end": 5, "start": 0, "resources": 4}, "Programming Job": {"end": 18, "start": 12, "resources": 4}}	2026-02-12 08:58:49.060074
12	{"Wood": {"end": 25, "start": 20, "resources": 3}, "jobA": {"end": 10, "start": 0, "resources": 1}, "jobB": {"end": 17, "start": 10, "resources": 3}, "jobC": {"end": 6, "start": 2, "resources": 7}, "jobD": {"end": 10, "start": 0, "resources": 3}, "jobE": {"end": 25, "start": 10, "resources": 1}, "jobF": {"end": 12, "start": 6, "resources": 4}, "Panting2": {"end": 40, "start": 25, "resources": 1}, "Production": {"end": 15, "start": 5, "resources": 6}, "Calculating": {"end": 20, "start": 17, "resources": 3}, "paintingJob": {"end": 5, "start": 0, "resources": 6}, "Assembly Job": {"end": 5, "start": 0, "resources": 4}, "Programming Job": {"end": 18, "start": 12, "resources": 4}}	2026-02-12 09:08:16.976609
13	{"Wood": {"end": 25, "start": 20, "resources": 3}, "jobA": {"end": 10, "start": 0, "resources": 1}, "jobB": {"end": 17, "start": 10, "resources": 3}, "jobC": {"end": 6, "start": 2, "resources": 7}, "jobD": {"end": 10, "start": 0, "resources": 3}, "jobE": {"end": 25, "start": 10, "resources": 1}, "jobF": {"end": 12, "start": 6, "resources": 4}, "Panting2": {"end": 40, "start": 25, "resources": 1}, "Production": {"end": 15, "start": 5, "resources": 6}, "Calculating": {"end": 20, "start": 17, "resources": 3}, "paintingJob": {"end": 5, "start": 0, "resources": 6}, "Assembly Job": {"end": 5, "start": 0, "resources": 4}, "Programming Job": {"end": 18, "start": 12, "resources": 4}}	2026-02-19 01:47:25.701244
14	{"Wood": {"end": 25, "start": 20, "resources": 3}, "jobA": {"end": 10, "start": 0, "resources": 1}, "jobB": {"end": 17, "start": 10, "resources": 3}, "jobC": {"end": 6, "start": 2, "resources": 7}, "jobD": {"end": 10, "start": 0, "resources": 3}, "jobE": {"end": 25, "start": 10, "resources": 1}, "jobF": {"end": 12, "start": 6, "resources": 4}, "Panting2": {"end": 40, "start": 25, "resources": 1}, "Production": {"end": 15, "start": 5, "resources": 6}, "Calculating": {"end": 20, "start": 17, "resources": 3}, "paintingJob": {"end": 5, "start": 0, "resources": 6}, "Assembly Job": {"end": 5, "start": 0, "resources": 4}, "Programming Job": {"end": 18, "start": 12, "resources": 4}}	2026-02-19 03:07:53.99359
\.


--
-- Name: ALLOWED_ON_id_seq; Type: SEQUENCE SET; Schema: production_graph; Owner: -
--

SELECT pg_catalog.setval('production_graph."ALLOWED_ON_id_seq"', 7, true);


--
-- Name: CAN_RUN_ON_id_seq; Type: SEQUENCE SET; Schema: production_graph; Owner: -
--

SELECT pg_catalog.setval('production_graph."CAN_RUN_ON_id_seq"', 7, true);


--
-- Name: Job_id_seq; Type: SEQUENCE SET; Schema: production_graph; Owner: -
--

SELECT pg_catalog.setval('production_graph."Job_id_seq"', 5, true);


--
-- Name: Machine_id_seq; Type: SEQUENCE SET; Schema: production_graph; Owner: -
--

SELECT pg_catalog.setval('production_graph."Machine_id_seq"', 3, true);


--
-- Name: Material_id_seq; Type: SEQUENCE SET; Schema: production_graph; Owner: -
--

SELECT pg_catalog.setval('production_graph."Material_id_seq"', 2, true);


--
-- Name: PRECEDES_id_seq; Type: SEQUENCE SET; Schema: production_graph; Owner: -
--

SELECT pg_catalog.setval('production_graph."PRECEDES_id_seq"', 2, true);


--
-- Name: _ag_label_edge_id_seq; Type: SEQUENCE SET; Schema: production_graph; Owner: -
--

SELECT pg_catalog.setval('production_graph._ag_label_edge_id_seq', 1, false);


--
-- Name: _ag_label_vertex_id_seq; Type: SEQUENCE SET; Schema: production_graph; Owner: -
--

SELECT pg_catalog.setval('production_graph._ag_label_vertex_id_seq', 1, false);


--
-- Name: _label_id_seq; Type: SEQUENCE SET; Schema: production_graph; Owner: -
--

SELECT pg_catalog.setval('production_graph._label_id_seq', 8, true);


--
-- Name: machine_types_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.machine_types_type_id_seq', 7, true);


--
-- Name: schedule_result_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.schedule_result_id_seq', 14, true);


--
-- Name: _ag_label_edge _ag_label_edge_pkey; Type: CONSTRAINT; Schema: production_graph; Owner: -
--

ALTER TABLE ONLY production_graph._ag_label_edge
    ADD CONSTRAINT _ag_label_edge_pkey PRIMARY KEY (id);


--
-- Name: _ag_label_vertex _ag_label_vertex_pkey; Type: CONSTRAINT; Schema: production_graph; Owner: -
--

ALTER TABLE ONLY production_graph._ag_label_vertex
    ADD CONSTRAINT _ag_label_vertex_pkey PRIMARY KEY (id);


--
-- Name: config config_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.config
    ADD CONSTRAINT config_pkey PRIMARY KEY (key);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (job_id);


--
-- Name: machine_types machine_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.machine_types
    ADD CONSTRAINT machine_types_pkey PRIMARY KEY (type_id);


--
-- Name: machine_types machine_types_type_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.machine_types
    ADD CONSTRAINT machine_types_type_name_key UNIQUE (type_name);


--
-- Name: machines machines_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.machines
    ADD CONSTRAINT machines_pkey PRIMARY KEY (machine_id);


--
-- Name: materials materials_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_pkey PRIMARY KEY (material_id);


--
-- Name: schedule_result schedule_result_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedule_result
    ADD CONSTRAINT schedule_result_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_required_machine_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_required_machine_type_id_fkey FOREIGN KEY (required_machine_type_id) REFERENCES public.machine_types(type_id);


--
-- Name: machines machines_machine_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.machines
    ADD CONSTRAINT machines_machine_type_id_fkey FOREIGN KEY (machine_type_id) REFERENCES public.machine_types(type_id);


--
-- PostgreSQL database dump complete
--

\unrestrict MwymxzVIFZ3YrUxnJv50HYG4qUw09tV9yDdhSgdbiYBQ86jA5mzEg7MU7ksVfcU

