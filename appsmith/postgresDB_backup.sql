--
-- PostgreSQL database dump
--

\restrict 4d9ZA2Tq8ih9VBYSjIrRGR9d09v5gpoRseWr7XukznVPXu7yQfgqT5yJ2xXUNdB

-- Dumped from database version 15.15 (Debian 15.15-1.pgdg13+1)
-- Dumped by pg_dump version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)

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
-- Name: inventory; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.inventory (
    item_id integer NOT NULL,
    item_name text NOT NULL,
    quantity integer NOT NULL,
    min_required integer NOT NULL,
    max_capacity integer NOT NULL,
    last_updated timestamp without time zone DEFAULT now(),
    received_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.inventory OWNER TO "postgresUser";

--
-- Name: inventory_item_id_seq; Type: SEQUENCE; Schema: public; Owner: postgresUser
--

CREATE SEQUENCE public.inventory_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.inventory_item_id_seq OWNER TO "postgresUser";

--
-- Name: inventory_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgresUser
--

ALTER SEQUENCE public.inventory_item_id_seq OWNED BY public.inventory.item_id;


--
-- Name: machines; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.machines (
    machine_id integer NOT NULL,
    name text NOT NULL,
    type text NOT NULL,
    capacity integer DEFAULT 1
);


ALTER TABLE public.machines OWNER TO "postgresUser";

--
-- Name: machines_machine_id_seq; Type: SEQUENCE; Schema: public; Owner: postgresUser
--

CREATE SEQUENCE public.machines_machine_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.machines_machine_id_seq OWNER TO "postgresUser";

--
-- Name: machines_machine_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgresUser
--

ALTER SEQUENCE public.machines_machine_id_seq OWNED BY public.machines.machine_id;


--
-- Name: operations; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.operations (
    operation_id integer NOT NULL,
    name text NOT NULL,
    duration integer NOT NULL,
    required_machine_type text NOT NULL,
    material_needed text
);


ALTER TABLE public.operations OWNER TO "postgresUser";

--
-- Name: operations_operation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgresUser
--

CREATE SEQUENCE public.operations_operation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.operations_operation_id_seq OWNER TO "postgresUser";

--
-- Name: operations_operation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgresUser
--

ALTER SEQUENCE public.operations_operation_id_seq OWNED BY public.operations.operation_id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.orders (
    order_id integer NOT NULL,
    product_name text,
    priority integer,
    due_date date,
    quantity integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.orders OWNER TO "postgresUser";

--
-- Name: orders_order_id_seq; Type: SEQUENCE; Schema: public; Owner: postgresUser
--

CREATE SEQUENCE public.orders_order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.orders_order_id_seq OWNER TO "postgresUser";

--
-- Name: orders_order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgresUser
--

ALTER SEQUENCE public.orders_order_id_seq OWNED BY public.orders.order_id;


--
-- Name: product_operations; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.product_operations (
    operation_id integer NOT NULL,
    sequence integer NOT NULL,
    product_id integer NOT NULL
);


ALTER TABLE public.product_operations OWNER TO "postgresUser";

--
-- Name: products; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.products (
    product_id integer NOT NULL,
    product_name text NOT NULL
);


ALTER TABLE public.products OWNER TO "postgresUser";

--
-- Name: product_operations_view; Type: VIEW; Schema: public; Owner: postgresUser
--

CREATE VIEW public.product_operations_view AS
 SELECT p.product_id,
    p.product_name,
    json_agg(json_build_object('operation_id', po.operation_id, 'operation_name', o.name, 'sequence', po.sequence) ORDER BY po.sequence) AS operations
   FROM ((public.product_operations po
     JOIN public.products p ON ((p.product_id = po.product_id)))
     JOIN public.operations o ON ((o.operation_id = po.operation_id)))
  GROUP BY p.product_id, p.product_name
  ORDER BY p.product_name;


ALTER VIEW public.product_operations_view OWNER TO "postgresUser";

--
-- Name: products_product_id_seq; Type: SEQUENCE; Schema: public; Owner: postgresUser
--

CREATE SEQUENCE public.products_product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_product_id_seq OWNER TO "postgresUser";

--
-- Name: products_product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgresUser
--

ALTER SEQUENCE public.products_product_id_seq OWNED BY public.products.product_id;


--
-- Name: schedule_archive; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.schedule_archive (
    archive_id integer NOT NULL,
    run_id uuid NOT NULL,
    order_id integer NOT NULL,
    operation text NOT NULL,
    machine text NOT NULL,
    start_offset integer,
    end_offset integer,
    start_ts timestamp without time zone,
    end_ts timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.schedule_archive OWNER TO "postgresUser";

--
-- Name: schedule_archive_archive_id_seq; Type: SEQUENCE; Schema: public; Owner: postgresUser
--

CREATE SEQUENCE public.schedule_archive_archive_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.schedule_archive_archive_id_seq OWNER TO "postgresUser";

--
-- Name: schedule_archive_archive_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgresUser
--

ALTER SEQUENCE public.schedule_archive_archive_id_seq OWNED BY public.schedule_archive.archive_id;


--
-- Name: schedule_results; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.schedule_results (
    schedule_id integer NOT NULL,
    order_id integer NOT NULL,
    operation character varying(50) NOT NULL,
    machine character varying(50) NOT NULL,
    start_offset integer NOT NULL,
    end_offset integer NOT NULL,
    start_ts timestamp without time zone NOT NULL,
    end_ts timestamp without time zone NOT NULL,
    run_id uuid,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.schedule_results OWNER TO "postgresUser";

--
-- Name: schedule_results_schedule_id_seq; Type: SEQUENCE; Schema: public; Owner: postgresUser
--

CREATE SEQUENCE public.schedule_results_schedule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.schedule_results_schedule_id_seq OWNER TO "postgresUser";

--
-- Name: schedule_results_schedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgresUser
--

ALTER SEQUENCE public.schedule_results_schedule_id_seq OWNED BY public.schedule_results.schedule_id;


--
-- Name: schedule_runs; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.schedule_runs (
    run_id uuid NOT NULL,
    run_time timestamp without time zone DEFAULT now(),
    note text
);


ALTER TABLE public.schedule_runs OWNER TO "postgresUser";

--
-- Name: inventory item_id; Type: DEFAULT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.inventory ALTER COLUMN item_id SET DEFAULT nextval('public.inventory_item_id_seq'::regclass);


--
-- Name: machines machine_id; Type: DEFAULT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.machines ALTER COLUMN machine_id SET DEFAULT nextval('public.machines_machine_id_seq'::regclass);


--
-- Name: operations operation_id; Type: DEFAULT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.operations ALTER COLUMN operation_id SET DEFAULT nextval('public.operations_operation_id_seq'::regclass);


--
-- Name: orders order_id; Type: DEFAULT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.orders ALTER COLUMN order_id SET DEFAULT nextval('public.orders_order_id_seq'::regclass);


--
-- Name: products product_id; Type: DEFAULT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.products ALTER COLUMN product_id SET DEFAULT nextval('public.products_product_id_seq'::regclass);


--
-- Name: schedule_archive archive_id; Type: DEFAULT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.schedule_archive ALTER COLUMN archive_id SET DEFAULT nextval('public.schedule_archive_archive_id_seq'::regclass);


--
-- Name: schedule_results schedule_id; Type: DEFAULT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.schedule_results ALTER COLUMN schedule_id SET DEFAULT nextval('public.schedule_results_schedule_id_seq'::regclass);


--
-- Data for Name: ag_graph; Type: TABLE DATA; Schema: ag_catalog; Owner: postgres
--

COPY ag_catalog.ag_graph (graphid, name, namespace) FROM stdin;
\.


--
-- Data for Name: ag_label; Type: TABLE DATA; Schema: ag_catalog; Owner: postgres
--

COPY ag_catalog.ag_label (name, graph, id, kind, relation, seq_name) FROM stdin;
\.


--
-- Data for Name: inventory; Type: TABLE DATA; Schema: public; Owner: postgresUser
--

COPY public.inventory (item_id, item_name, quantity, min_required, max_capacity, last_updated, received_at) FROM stdin;
1	Testing Item1	5	1	100	2025-12-16 06:59:24.089572	2025-12-16 06:59:24.089572
2	Metal	10	5	20	2025-12-16 09:01:03.608319	2025-12-16 09:01:03.608319
\.


--
-- Data for Name: machines; Type: TABLE DATA; Schema: public; Owner: postgresUser
--

COPY public.machines (machine_id, name, type, capacity) FROM stdin;
1	Cutter1	Cutting	1
2	Assembler1	Assembly	1
3	Painter1	Painting	1
4	Cutter2	Cutting	1
5	Assembler2	Assembly	1
6	Painter2	Painting	1
\.


--
-- Data for Name: operations; Type: TABLE DATA; Schema: public; Owner: postgresUser
--

COPY public.operations (operation_id, name, duration, required_machine_type, material_needed) FROM stdin;
1	Cutting	2	Cutting	\N
2	Assembling	3	Assembly	\N
3	Painting	1	Painting	\N
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: postgresUser
--

COPY public.orders (order_id, product_name, priority, due_date, quantity) FROM stdin;
1	Widget A	1	2025-12-20	5
2	Widget B	2	2025-12-22	3
\.


--
-- Data for Name: product_operations; Type: TABLE DATA; Schema: public; Owner: postgresUser
--

COPY public.product_operations (operation_id, sequence, product_id) FROM stdin;
3	1	1
1	2	1
2	3	1
1	1	2
2	2	2
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgresUser
--

COPY public.products (product_id, product_name) FROM stdin;
1	Widget B
2	Widget A
5	Widget C
\.


--
-- Data for Name: schedule_archive; Type: TABLE DATA; Schema: public; Owner: postgresUser
--

COPY public.schedule_archive (archive_id, run_id, order_id, operation, machine, start_offset, end_offset, start_ts, end_ts, created_at) FROM stdin;
\.


--
-- Data for Name: schedule_results; Type: TABLE DATA; Schema: public; Owner: postgresUser
--

COPY public.schedule_results (schedule_id, order_id, operation, machine, start_offset, end_offset, start_ts, end_ts, run_id, created_at) FROM stdin;
73	1	Cutting	Cutter1	2	4	2025-12-18 02:00:00	2025-12-18 04:00:00	3d931018-74c3-4802-9783-1443c6a87db8	2025-12-18 05:29:15.588326
74	1	Assembling	Assembler1	5	8	2025-12-18 05:00:00	2025-12-18 08:00:00	3d931018-74c3-4802-9783-1443c6a87db8	2025-12-18 05:29:15.588326
75	1	Painting	Painter1	8	9	2025-12-18 08:00:00	2025-12-18 09:00:00	3d931018-74c3-4802-9783-1443c6a87db8	2025-12-18 05:29:15.588326
76	2	Cutting	Cutter1	0	2	2025-12-18 00:00:00	2025-12-18 02:00:00	3d931018-74c3-4802-9783-1443c6a87db8	2025-12-18 05:29:15.588326
77	2	Assembling	Assembler1	2	5	2025-12-18 02:00:00	2025-12-18 05:00:00	3d931018-74c3-4802-9783-1443c6a87db8	2025-12-18 05:29:15.588326
78	2	Painting	Painter1	5	6	2025-12-18 05:00:00	2025-12-18 06:00:00	3d931018-74c3-4802-9783-1443c6a87db8	2025-12-18 05:29:15.588326
\.


--
-- Data for Name: schedule_runs; Type: TABLE DATA; Schema: public; Owner: postgresUser
--

COPY public.schedule_runs (run_id, run_time, note) FROM stdin;
609796d6-2778-4f56-895a-dc77c06f2c03	2025-12-16 03:47:59.659213	\N
0ec59b35-4050-4794-a7eb-67d3881d3392	2025-12-16 03:48:23.57429	\N
1f5e50b4-ea8f-4f1a-ab04-d2c787602a8d	2025-12-16 08:21:02.143661	\N
851efabe-2284-48cf-a366-3ade3f06917b	2025-12-16 08:21:09.223149	\N
0908cd50-e31c-4324-968a-791203edb445	2025-12-16 08:21:26.790786	\N
26d9b55a-d16a-4509-90a2-90b17ff7a8bb	2025-12-16 08:22:35.938354	\N
9cce325a-6086-454c-8231-7fbb30084cc1	2025-12-16 08:23:21.970873	\N
75db12b0-e7a5-4a23-90fa-630961b48592	2025-12-16 08:23:23.962289	\N
15d42670-e48c-4212-8d4c-1a1dee8579aa	2025-12-16 08:24:46.984519	\N
fa3855b6-49b6-4315-aebf-8000fd018e7a	2025-12-16 08:24:48.493326	\N
14cb51d2-b993-40a8-84a0-284354f37045	2025-12-16 08:25:01.917626	\N
777c8402-eda2-451c-9ad9-20daf8056275	2025-12-16 08:26:04.098246	\N
6e625ce5-d536-44e1-b81d-fa2cd9fe5268	2025-12-16 08:26:18.675317	\N
d3cbc116-cdc9-48f2-a7f7-76455768e818	2025-12-16 08:26:19.583036	\N
72623296-d3ff-459f-a8c9-f8e221f11d53	2025-12-16 08:26:29.923954	\N
6fcb587d-1508-4407-b866-2106fb022165	2025-12-16 08:30:58.878516	\N
5ba8194a-eb74-44f0-be4d-c1267be5ec20	2025-12-16 08:34:14.566596	\N
bb264873-3021-4d7b-9182-a893f0ee589d	2025-12-16 08:42:45.185123	\N
b70bdf8a-26f3-43b2-98d3-9dfe1444bcf7	2025-12-16 08:43:26.250545	\N
737f81dc-8abd-4ad2-bd60-ffb3b4ec0684	2025-12-18 02:01:33.695029	\N
d09ac706-eca3-4be7-af16-0ba2c7497315	2025-12-18 02:08:15.504992	\N
af1a3906-2ac2-41cf-9434-17e86b714414	2025-12-18 03:29:45.153362	\N
6bdaea0d-ee6f-43d2-93bf-c6dce883edab	2025-12-18 03:29:49.81704	\N
eb6fe16e-bc32-4d62-b440-dd60f250ad5d	2025-12-18 04:08:48.358668	\N
15f4e35f-f068-4341-b51c-30b854665458	2025-12-18 05:22:51.016894	\N
3d931018-74c3-4802-9783-1443c6a87db8	2025-12-18 05:29:15.615769	\N
\.


--
-- Name: inventory_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgresUser
--

SELECT pg_catalog.setval('public.inventory_item_id_seq', 2, true);


--
-- Name: machines_machine_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgresUser
--

SELECT pg_catalog.setval('public.machines_machine_id_seq', 6, true);


--
-- Name: operations_operation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgresUser
--

SELECT pg_catalog.setval('public.operations_operation_id_seq', 3, true);


--
-- Name: orders_order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgresUser
--

SELECT pg_catalog.setval('public.orders_order_id_seq', 2, true);


--
-- Name: products_product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgresUser
--

SELECT pg_catalog.setval('public.products_product_id_seq', 5, true);


--
-- Name: schedule_archive_archive_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgresUser
--

SELECT pg_catalog.setval('public.schedule_archive_archive_id_seq', 1, false);


--
-- Name: schedule_results_schedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgresUser
--

SELECT pg_catalog.setval('public.schedule_results_schedule_id_seq', 78, true);


--
-- Name: inventory inventory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_pkey PRIMARY KEY (item_id);


--
-- Name: machines machines_pkey; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.machines
    ADD CONSTRAINT machines_pkey PRIMARY KEY (machine_id);


--
-- Name: operations operations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.operations
    ADD CONSTRAINT operations_pkey PRIMARY KEY (operation_id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (order_id);


--
-- Name: product_operations product_operations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.product_operations
    ADD CONSTRAINT product_operations_pkey PRIMARY KEY (product_id, operation_id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (product_id);


--
-- Name: products products_product_name_key; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_product_name_key UNIQUE (product_name);


--
-- Name: schedule_archive schedule_archive_pkey; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.schedule_archive
    ADD CONSTRAINT schedule_archive_pkey PRIMARY KEY (archive_id);


--
-- Name: schedule_results schedule_results_pkey; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.schedule_results
    ADD CONSTRAINT schedule_results_pkey PRIMARY KEY (schedule_id);


--
-- Name: schedule_runs schedule_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.schedule_runs
    ADD CONSTRAINT schedule_runs_pkey PRIMARY KEY (run_id);


--
-- Name: idx_product_operations_operation_id; Type: INDEX; Schema: public; Owner: postgresUser
--

CREATE INDEX idx_product_operations_operation_id ON public.product_operations USING btree (operation_id);


--
-- Name: idx_product_operations_product_id; Type: INDEX; Schema: public; Owner: postgresUser
--

CREATE INDEX idx_product_operations_product_id ON public.product_operations USING btree (product_id);


--
-- Name: ux_product_operation; Type: INDEX; Schema: public; Owner: postgresUser
--

CREATE UNIQUE INDEX ux_product_operation ON public.product_operations USING btree (product_id, operation_id);


--
-- Name: product_operations fk_product; Type: FK CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.product_operations
    ADD CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES public.products(product_id) ON DELETE CASCADE;


--
-- Name: product_operations product_operations_operation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.product_operations
    ADD CONSTRAINT product_operations_operation_id_fkey FOREIGN KEY (operation_id) REFERENCES public.operations(operation_id);


--
-- Name: schedule_results schedule_results_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.schedule_results
    ADD CONSTRAINT schedule_results_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id);


--
-- PostgreSQL database dump complete
--

\unrestrict 4d9ZA2Tq8ih9VBYSjIrRGR9d09v5gpoRseWr7XukznVPXu7yQfgqT5yJ2xXUNdB

