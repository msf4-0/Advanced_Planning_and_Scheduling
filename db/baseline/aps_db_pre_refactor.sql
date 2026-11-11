--
-- PostgreSQL database dump
--

\restrict ZOe1zR2u1UbXIOdiHDzfGLhsFxb4wrfBl7KglSkssgQRUxLqBrtsEfezn3Z5DZH

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: factory_holidays; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.factory_holidays (
    id integer NOT NULL,
    holiday_date date NOT NULL,
    description character varying(100)
);


--
-- Name: TABLE factory_holidays; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.factory_holidays IS 'Global blackout dates representing factory closures where all processing variables are strictly frozen.';


--
-- Name: factory_holidays_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.factory_holidays_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: factory_holidays_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.factory_holidays_id_seq OWNED BY public.factory_holidays.id;


--
-- Name: factory_shifts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.factory_shifts (
    id integer NOT NULL,
    resource_id character varying(50),
    day_of_week integer NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    CONSTRAINT factory_shifts_day_of_week_check CHECK (((day_of_week >= 1) AND (day_of_week <= 7)))
);


--
-- Name: TABLE factory_shifts; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.factory_shifts IS 'Operational working time parameters defining resource runtime availability ranges across the weekly horizon.';


--
-- Name: factory_shifts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.factory_shifts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: factory_shifts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.factory_shifts_id_seq OWNED BY public.factory_shifts.id;


--
-- Name: items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.items (
    id character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    sku character varying(50) NOT NULL
);


--
-- Name: TABLE items; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.items IS 'The item master master definition catalog profile storing finished product templates.';


--
-- Name: materials; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.materials (
    id character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    quantity_available numeric(12,4) DEFAULT 0.0,
    available_date_minutes integer DEFAULT 0
);


--
-- Name: TABLE materials; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.materials IS 'Raw raw stock material tracking registry ledger used for bill-of-materials restriction lookups.';


--
-- Name: COLUMN materials.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.materials.id IS 'Unique material stock keeping code identifier. Maps to the Item Code properties in ERPNext.';


--
-- Name: COLUMN materials.quantity_available; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.materials.quantity_available IS 'The raw numeric current physical stock level available immediately inside warehouse storage containers.';


--
-- Name: COLUMN materials.available_date_minutes; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.materials.available_date_minutes IS 'Calculated timeline arrival offset integer representing when upcoming purchase receipts land on disk.';


--
-- Name: operation_dependencies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.operation_dependencies (
    upstream_op_id character varying(50) NOT NULL,
    downstream_op_id character varying(50) NOT NULL
);


--
-- Name: TABLE operation_dependencies; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.operation_dependencies IS 'The multi-dependency network adjacency matrix storing directed acyclic graph (DAG) connection pointers.';


--
-- Name: COLUMN operation_dependencies.upstream_op_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.operation_dependencies.upstream_op_id IS 'The source operation block task required to finish executing first before unlocking the subsequent child node path.';


--
-- Name: COLUMN operation_dependencies.downstream_op_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.operation_dependencies.downstream_op_id IS 'The destination dependent operation step blocked until the preceding parental processing window collapses.';


--
-- Name: operation_materials; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.operation_materials (
    operation_id character varying(50) NOT NULL,
    material_id character varying(50) NOT NULL,
    quantity_required numeric(12,4) NOT NULL
);


--
-- Name: TABLE operation_materials; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.operation_materials IS 'Junction profile link defining specific bill of materials inventory draw demands for particular operations.';


--
-- Name: operations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.operations (
    id character varying(50) NOT NULL,
    work_order_id character varying(50),
    sequence_number integer NOT NULL,
    duration_minutes integer NOT NULL,
    assigned_resource_id character varying(50),
    status character varying(20) DEFAULT 'Draft'::character varying
);


--
-- Name: TABLE operations; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.operations IS 'Individual step-by-step processing tasks that populate active memory as ProcessNode graph objects.';


--
-- Name: COLUMN operations.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.operations.id IS 'Unique child operation step primary key. Instantiated via ERPNext child table operation row hashes.';


--
-- Name: COLUMN operations.sequence_number; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.operations.sequence_number IS 'The engineering workflow route processing hierarchy priority order index (e.g., 10, 20, 30).';


--
-- Name: COLUMN operations.duration_minutes; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.operations.duration_minutes IS 'The raw processing runtime capacity window required to execute the job task step block.';


--
-- Name: COLUMN operations.status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.operations.status IS 'The active execution state of this individual task step. Tracking values include: Draft, Scheduled, In Progress, Done.';


--
-- Name: resources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.resources (
    id character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    resource_type character varying(50) DEFAULT 'Machine'::character varying,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE resources; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.resources IS 'Physical production assets and shop floor capacities capable of executing factory routing tasks.';


--
-- Name: COLUMN resources.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.resources.id IS 'Unique identifier for the work center. Maps to ResourceNode.id (e.g., workstation name from ERPNext).';


--
-- Name: COLUMN resources.resource_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.resources.resource_type IS 'The resource categorization boundary. Acceptable types include: Machine, Human, Tooling.';


--
-- Name: COLUMN resources.is_active; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.resources.is_active IS 'Toggle constraint flag to temporarily remove broken or unavailable assets from the solver view.';


--
-- Name: routing_templates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.routing_templates (
    id integer NOT NULL,
    target_item_id character varying(50),
    step_sequence integer NOT NULL,
    required_resource_type character varying(50) NOT NULL,
    standard_duration_minutes integer NOT NULL
);


--
-- Name: TABLE routing_templates; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.routing_templates IS 'Engineering blueprint masters used to auto-generate baseline operations arrays whenever a fresh manufacturing request arrives.';


--
-- Name: routing_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.routing_templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: routing_templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.routing_templates_id_seq OWNED BY public.routing_templates.id;


--
-- Name: scheduled_tasks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.scheduled_tasks (
    id integer NOT NULL,
    run_id integer NOT NULL,
    operation_id character varying(50) NOT NULL,
    optimized_start_minute integer NOT NULL,
    optimized_end_minute integer NOT NULL,
    scheduled_start_time timestamp without time zone NOT NULL,
    scheduled_end_time timestamp without time zone NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: scheduled_tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.scheduled_tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: scheduled_tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.scheduled_tasks_id_seq OWNED BY public.scheduled_tasks.id;


--
-- Name: scheduling_runs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.scheduling_runs (
    id integer NOT NULL,
    triggered_by integer,
    run_status character varying(20) NOT NULL,
    started_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    completed_at timestamp without time zone,
    log_messages text
);


--
-- Name: TABLE scheduling_runs; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.scheduling_runs IS 'System audit history tracking logs recording calculation run states, duration markers, and solver exceptions.';


--
-- Name: scheduling_runs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.scheduling_runs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: scheduling_runs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.scheduling_runs_id_seq OWNED BY public.scheduling_runs.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(20) DEFAULT 'Planner'::character varying
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: work_orders; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.work_orders (
    id character varying(50) NOT NULL,
    target_item_id character varying(50) NOT NULL,
    quantity_to_make integer NOT NULL,
    due_date timestamp without time zone NOT NULL,
    status character varying(20) DEFAULT 'Draft'::character varying
);


--
-- Name: TABLE work_orders; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.work_orders IS 'The ultimate parent customer demand orders anchoring manufacturing requirements.';


--
-- Name: COLUMN work_orders.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.work_orders.id IS 'Primary Work Order sequence code key (e.g., standard serialized nomenclature MFG-WO-2026-00001).';


--
-- Name: COLUMN work_orders.due_date; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.work_orders.due_date IS 'The ultimate customer delivery deadline used by the solver objective loop to calculate total system lateness.';


--
-- Name: COLUMN work_orders.status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.work_orders.status IS 'Transactional state lifecycles: Draft, Approved, Scheduled, In Progress, Done.';


--
-- Name: factory_holidays id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.factory_holidays ALTER COLUMN id SET DEFAULT nextval('public.factory_holidays_id_seq'::regclass);


--
-- Name: factory_shifts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.factory_shifts ALTER COLUMN id SET DEFAULT nextval('public.factory_shifts_id_seq'::regclass);


--
-- Name: routing_templates id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.routing_templates ALTER COLUMN id SET DEFAULT nextval('public.routing_templates_id_seq'::regclass);


--
-- Name: scheduled_tasks id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduled_tasks ALTER COLUMN id SET DEFAULT nextval('public.scheduled_tasks_id_seq'::regclass);


--
-- Name: scheduling_runs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduling_runs ALTER COLUMN id SET DEFAULT nextval('public.scheduling_runs_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: factory_holidays; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.factory_holidays (id, holiday_date, description) FROM stdin;
\.


--
-- Data for Name: factory_shifts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.factory_shifts (id, resource_id, day_of_week, start_time, end_time) FROM stdin;
\.


--
-- Data for Name: items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.items (id, name, sku) FROM stdin;
\.


--
-- Data for Name: materials; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.materials (id, name, quantity_available, available_date_minutes) FROM stdin;
\.


--
-- Data for Name: operation_dependencies; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.operation_dependencies (upstream_op_id, downstream_op_id) FROM stdin;
\.


--
-- Data for Name: operation_materials; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.operation_materials (operation_id, material_id, quantity_required) FROM stdin;
\.


--
-- Data for Name: operations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.operations (id, work_order_id, sequence_number, duration_minutes, assigned_resource_id, status) FROM stdin;
\.


--
-- Data for Name: resources; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.resources (id, name, resource_type, is_active, created_at) FROM stdin;
\.


--
-- Data for Name: routing_templates; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.routing_templates (id, target_item_id, step_sequence, required_resource_type, standard_duration_minutes) FROM stdin;
\.


--
-- Data for Name: scheduled_tasks; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.scheduled_tasks (id, run_id, operation_id, optimized_start_minute, optimized_end_minute, scheduled_start_time, scheduled_end_time, created_at) FROM stdin;
\.


--
-- Data for Name: scheduling_runs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.scheduling_runs (id, triggered_by, run_status, started_at, completed_at, log_messages) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, username, password_hash, role) FROM stdin;
\.


--
-- Data for Name: work_orders; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.work_orders (id, target_item_id, quantity_to_make, due_date, status) FROM stdin;
\.


--
-- Name: factory_holidays_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.factory_holidays_id_seq', 1, false);


--
-- Name: factory_shifts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.factory_shifts_id_seq', 1, false);


--
-- Name: routing_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.routing_templates_id_seq', 1, false);


--
-- Name: scheduled_tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.scheduled_tasks_id_seq', 1, false);


--
-- Name: scheduling_runs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.scheduling_runs_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: factory_holidays factory_holidays_holiday_date_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.factory_holidays
    ADD CONSTRAINT factory_holidays_holiday_date_key UNIQUE (holiday_date);


--
-- Name: factory_holidays factory_holidays_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.factory_holidays
    ADD CONSTRAINT factory_holidays_pkey PRIMARY KEY (id);


--
-- Name: factory_shifts factory_shifts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.factory_shifts
    ADD CONSTRAINT factory_shifts_pkey PRIMARY KEY (id);


--
-- Name: items items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_pkey PRIMARY KEY (id);


--
-- Name: items items_sku_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_sku_key UNIQUE (sku);


--
-- Name: materials materials_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_pkey PRIMARY KEY (id);


--
-- Name: operation_dependencies operation_dependencies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operation_dependencies
    ADD CONSTRAINT operation_dependencies_pkey PRIMARY KEY (upstream_op_id, downstream_op_id);


--
-- Name: operation_materials operation_materials_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operation_materials
    ADD CONSTRAINT operation_materials_pkey PRIMARY KEY (operation_id, material_id);


--
-- Name: operations operations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operations
    ADD CONSTRAINT operations_pkey PRIMARY KEY (id);


--
-- Name: resources resources_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.resources
    ADD CONSTRAINT resources_pkey PRIMARY KEY (id);


--
-- Name: routing_templates routing_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.routing_templates
    ADD CONSTRAINT routing_templates_pkey PRIMARY KEY (id);


--
-- Name: scheduled_tasks scheduled_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduled_tasks
    ADD CONSTRAINT scheduled_tasks_pkey PRIMARY KEY (id);


--
-- Name: scheduling_runs scheduling_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduling_runs
    ADD CONSTRAINT scheduling_runs_pkey PRIMARY KEY (id);


--
-- Name: scheduled_tasks uniq_run_operation; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduled_tasks
    ADD CONSTRAINT uniq_run_operation UNIQUE (run_id, operation_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: work_orders work_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.work_orders
    ADD CONSTRAINT work_orders_pkey PRIMARY KEY (id);


--
-- Name: factory_shifts factory_shifts_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.factory_shifts
    ADD CONSTRAINT factory_shifts_resource_id_fkey FOREIGN KEY (resource_id) REFERENCES public.resources(id) ON DELETE CASCADE;


--
-- Name: operation_dependencies operation_dependencies_downstream_op_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operation_dependencies
    ADD CONSTRAINT operation_dependencies_downstream_op_id_fkey FOREIGN KEY (downstream_op_id) REFERENCES public.operations(id) ON DELETE CASCADE;


--
-- Name: operation_dependencies operation_dependencies_upstream_op_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operation_dependencies
    ADD CONSTRAINT operation_dependencies_upstream_op_id_fkey FOREIGN KEY (upstream_op_id) REFERENCES public.operations(id) ON DELETE CASCADE;


--
-- Name: operation_materials operation_materials_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operation_materials
    ADD CONSTRAINT operation_materials_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(id) ON DELETE CASCADE;


--
-- Name: operation_materials operation_materials_operation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operation_materials
    ADD CONSTRAINT operation_materials_operation_id_fkey FOREIGN KEY (operation_id) REFERENCES public.operations(id) ON DELETE CASCADE;


--
-- Name: operations operations_assigned_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operations
    ADD CONSTRAINT operations_assigned_resource_id_fkey FOREIGN KEY (assigned_resource_id) REFERENCES public.resources(id);


--
-- Name: operations operations_work_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operations
    ADD CONSTRAINT operations_work_order_id_fkey FOREIGN KEY (work_order_id) REFERENCES public.work_orders(id) ON DELETE CASCADE;


--
-- Name: routing_templates routing_templates_target_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.routing_templates
    ADD CONSTRAINT routing_templates_target_item_id_fkey FOREIGN KEY (target_item_id) REFERENCES public.items(id) ON DELETE CASCADE;


--
-- Name: scheduled_tasks scheduled_tasks_operation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduled_tasks
    ADD CONSTRAINT scheduled_tasks_operation_id_fkey FOREIGN KEY (operation_id) REFERENCES public.operations(id) ON DELETE CASCADE;


--
-- Name: scheduled_tasks scheduled_tasks_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduled_tasks
    ADD CONSTRAINT scheduled_tasks_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.scheduling_runs(id) ON DELETE CASCADE;


--
-- Name: scheduling_runs scheduling_runs_triggered_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduling_runs
    ADD CONSTRAINT scheduling_runs_triggered_by_fkey FOREIGN KEY (triggered_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict ZOe1zR2u1UbXIOdiHDzfGLhsFxb4wrfBl7KglSkssgQRUxLqBrtsEfezn3Z5DZH

