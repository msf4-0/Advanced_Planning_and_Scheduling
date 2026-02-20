--
-- PostgreSQL database dump
--

\restrict FEeeKWLoGF43iyJuuS6PremWS2EDWrbXe6vPs8ZZQrnXE8PhzIf6zsnJGfLCOQY

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


ALTER SEQUENCE production_graph."ALLOWED_ON_id_seq" OWNER TO "postgresUser";

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


ALTER SEQUENCE production_graph."CAN_RUN_ON_id_seq" OWNER TO "postgresUser";

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


ALTER SEQUENCE production_graph."Job_id_seq" OWNER TO "postgresUser";

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


ALTER SEQUENCE production_graph."Machine_id_seq" OWNER TO "postgresUser";

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


ALTER SEQUENCE production_graph."Material_id_seq" OWNER TO "postgresUser";

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


ALTER SEQUENCE production_graph."PRECEDES_id_seq" OWNER TO "postgresUser";

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


ALTER SEQUENCE production_graph._ag_label_edge_id_seq OWNER TO "postgresUser";

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


ALTER SEQUENCE production_graph._ag_label_vertex_id_seq OWNER TO "postgresUser";

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


ALTER SEQUENCE production_graph._label_id_seq OWNER TO "postgresUser";

--
-- Name: New_table2; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public."New_table2" (
    id integer NOT NULL,
    client character varying(255)
);


ALTER TABLE public."New_table2" OWNER TO "postgresUser";

--
-- Name: New_table2_id_seq; Type: SEQUENCE; Schema: public; Owner: postgresUser
--

CREATE SEQUENCE public."New_table2_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."New_table2_id_seq" OWNER TO "postgresUser";

--
-- Name: New_table2_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgresUser
--

ALTER SEQUENCE public."New_table2_id_seq" OWNED BY public."New_table2".id;


--
-- Name: config; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.config (
    key text NOT NULL,
    value text
);


ALTER TABLE public.config OWNER TO "postgresUser";

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


ALTER SEQUENCE public.machine_types_type_id_seq OWNER TO "postgresUser";

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


ALTER SEQUENCE public.new_table_id_seq OWNER TO "postgresUser";

--
-- Name: new_table_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgresUser
--

ALTER SEQUENCE public.new_table_id_seq OWNED BY public.new_table.id;


--
-- Name: schedule_result; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.schedule_result (
    id integer NOT NULL,
    result jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.schedule_result OWNER TO "postgresUser";

--
-- Name: schedule_result_id_seq; Type: SEQUENCE; Schema: public; Owner: postgresUser
--

CREATE SEQUENCE public.schedule_result_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.schedule_result_id_seq OWNER TO "postgresUser";

--
-- Name: schedule_result_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgresUser
--

ALTER SEQUENCE public.schedule_result_id_seq OWNED BY public.schedule_result.id;


--
-- Name: tabCompany; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public."tabCompany" (
    name character varying(140) NOT NULL,
    creation timestamp without time zone,
    modified timestamp without time zone,
    modified_by character varying(140),
    owner character varying(140),
    docstatus integer DEFAULT 0 NOT NULL,
    idx integer DEFAULT 0 NOT NULL,
    company_name character varying(140),
    abbr character varying(140),
    default_currency character varying(140),
    country character varying(140),
    is_group integer DEFAULT 0 NOT NULL,
    default_holiday_list character varying(140),
    default_letter_head character varying(140),
    tax_id character varying(140),
    domain character varying(140),
    date_of_establishment date,
    parent_company character varying(140),
    company_logo text,
    date_of_incorporation date,
    phone_no character varying(140),
    email character varying(140),
    company_description text,
    date_of_commencement date,
    fax character varying(140),
    website character varying(140),
    registration_details text,
    lft integer DEFAULT 0 NOT NULL,
    rgt integer DEFAULT 0 NOT NULL,
    old_parent character varying(140),
    create_chart_of_accounts_based_on character varying(140),
    existing_company character varying(140),
    chart_of_accounts character varying(140),
    default_bank_account character varying(140),
    default_cash_account character varying(140),
    default_receivable_account character varying(140),
    round_off_account character varying(140),
    round_off_cost_center character varying(140),
    write_off_account character varying(140),
    exchange_gain_loss_account character varying(140),
    unrealized_exchange_gain_loss_account character varying(140),
    unrealized_profit_loss_account character varying(140),
    allow_account_creation_against_child_company integer DEFAULT 0 NOT NULL,
    default_payable_account character varying(140),
    default_expense_account character varying(140),
    default_income_account character varying(140),
    default_deferred_revenue_account character varying(140),
    default_deferred_expense_account character varying(140),
    default_discount_account character varying(140),
    payment_terms character varying(140),
    cost_center character varying(140),
    default_finance_book character varying(140),
    book_advance_payments_in_separate_party_account integer DEFAULT 0 NOT NULL,
    default_advance_received_account character varying(140),
    default_advance_paid_account character varying(140),
    auto_exchange_rate_revaluation integer DEFAULT 0 NOT NULL,
    auto_err_frequency character varying(140),
    submit_err_jv integer DEFAULT 0 NOT NULL,
    exception_budget_approver_role character varying(140),
    accumulated_depreciation_account character varying(140),
    depreciation_expense_account character varying(140),
    series_for_depreciation_entry character varying(140),
    expenses_included_in_asset_valuation character varying(140),
    disposal_account character varying(140),
    depreciation_cost_center character varying(140),
    capital_work_in_progress_account character varying(140),
    asset_received_but_not_billed character varying(140),
    default_buying_terms character varying(140),
    sales_monthly_history text,
    monthly_sales_target numeric(21,9) DEFAULT 0.000000000 NOT NULL,
    total_monthly_sales numeric(21,9) DEFAULT 0.000000000 NOT NULL,
    default_selling_terms character varying(140),
    default_warehouse_for_sales_return character varying(140),
    credit_limit numeric(21,9) DEFAULT 0.000000000 NOT NULL,
    transactions_annual_history text,
    enable_perpetual_inventory integer DEFAULT 1 NOT NULL,
    enable_provisional_accounting_for_non_stock_items integer DEFAULT 0 NOT NULL,
    default_inventory_account character varying(140),
    stock_adjustment_account character varying(140),
    default_in_transit_warehouse character varying(140),
    stock_received_but_not_billed character varying(140),
    default_provisional_account character varying(140),
    expenses_included_in_valuation character varying(140),
    _user_tags text,
    _comments text,
    _assign text,
    _liked_by text
);


ALTER TABLE public."tabCompany" OWNER TO "postgresUser";

--
-- Name: tabJob Card; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public."tabJob Card" (
    name character varying(140) NOT NULL,
    creation timestamp without time zone,
    modified timestamp without time zone,
    modified_by character varying(140),
    owner character varying(140),
    docstatus integer DEFAULT 0 NOT NULL,
    idx integer DEFAULT 0 NOT NULL,
    naming_series character varying(140) DEFAULT 'PO-JOB.#####'::character varying,
    work_order character varying(140),
    bom_no character varying(140),
    production_item character varying(140),
    posting_date date,
    company character varying(140),
    for_quantity numeric(21,9) DEFAULT 0.000000000 NOT NULL,
    total_completed_qty numeric(21,9) DEFAULT 0.000000000 NOT NULL,
    process_loss_qty numeric(21,9) DEFAULT 0.000000000 NOT NULL,
    expected_start_date timestamp without time zone,
    time_required numeric(21,9) DEFAULT 0.000000000 NOT NULL,
    expected_end_date timestamp without time zone,
    actual_start_date timestamp without time zone,
    total_time_in_mins numeric(21,9) DEFAULT 0.000000000 NOT NULL,
    actual_end_date timestamp without time zone,
    operation character varying(140),
    wip_warehouse character varying(140),
    workstation_type character varying(140),
    workstation character varying(140),
    quality_inspection_template character varying(140),
    quality_inspection character varying(140),
    for_job_card character varying(140),
    is_corrective_job_card integer DEFAULT 0 NOT NULL,
    hour_rate numeric(21,9) DEFAULT 0.000000000 NOT NULL,
    for_operation character varying(140),
    project character varying(140),
    item_name character varying(140),
    transferred_qty numeric(21,9) DEFAULT 0.000000000 NOT NULL,
    requested_qty numeric(21,9) DEFAULT 0.000000000 NOT NULL,
    status character varying(140) DEFAULT 'Open'::character varying,
    operation_row_number character varying(140),
    operation_id character varying(140),
    sequence_id integer DEFAULT 0 NOT NULL,
    remarks text,
    serial_and_batch_bundle character varying(140),
    batch_no character varying(140),
    serial_no text,
    barcode text,
    job_started integer DEFAULT 0 NOT NULL,
    started_time timestamp without time zone,
    "current_time" integer DEFAULT 0 NOT NULL,
    amended_from character varying(140),
    _user_tags text,
    _comments text,
    _assign text,
    _liked_by text
);


ALTER TABLE public."tabJob Card" OWNER TO "postgresUser";

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
-- Name: New_table2 id; Type: DEFAULT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public."New_table2" ALTER COLUMN id SET DEFAULT nextval('public."New_table2_id_seq"'::regclass);


--
-- Name: machine_types type_id; Type: DEFAULT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.machine_types ALTER COLUMN type_id SET DEFAULT nextval('public.machine_types_type_id_seq'::regclass);


--
-- Name: new_table id; Type: DEFAULT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.new_table ALTER COLUMN id SET DEFAULT nextval('public.new_table_id_seq'::regclass);


--
-- Name: schedule_result id; Type: DEFAULT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.schedule_result ALTER COLUMN id SET DEFAULT nextval('public.schedule_result_id_seq'::regclass);


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
-- Name: config config_pkey; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.config
    ADD CONSTRAINT config_pkey PRIMARY KEY (key);


--
-- Name: config seed values; Type: DATA; Schema: public; Owner: postgresUser
--

INSERT INTO public.config (key, value)
VALUES
    ('toggle_autoRun', 'TRUE'),
    ('job_tableName', 'jobs')
ON CONFLICT (key) DO UPDATE
SET value = EXCLUDED.value;


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
-- Name: schedule_result schedule_result_pkey; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.schedule_result
    ADD CONSTRAINT schedule_result_pkey PRIMARY KEY (id);


--
-- Name: tabCompany tabCompany_pkey; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public."tabCompany"
    ADD CONSTRAINT "tabCompany_pkey" PRIMARY KEY (name);


--
-- Name: tabJob Card tabJob Card_pkey; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public."tabJob Card"
    ADD CONSTRAINT "tabJob Card_pkey" PRIMARY KEY (name);


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

\unrestrict FEeeKWLoGF43iyJuuS6PremWS2EDWrbXe6vPs8ZZQrnXE8PhzIf6zsnJGfLCOQY

