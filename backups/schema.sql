--
-- PostgreSQL database dump
--

\restrict Iew6i0lVkMfUea3PqtFAULTv4OGpGcd6b6YoVMPIaNlhz9yVVacffhYCXoO4lNr

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
-- Name: DOES; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph."DOES" (
)
INHERITS (production_graph._ag_label_edge);


ALTER TABLE production_graph."DOES" OWNER TO "postgresUser";

--
-- Name: DOES_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph."DOES_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER SEQUENCE production_graph."DOES_id_seq" OWNER TO "postgresUser";

--
-- Name: DOES_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph."DOES_id_seq" OWNED BY production_graph."DOES".id;


--
-- Name: HAS_OPERATION; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph."HAS_OPERATION" (
)
INHERITS (production_graph._ag_label_edge);


ALTER TABLE production_graph."HAS_OPERATION" OWNER TO "postgresUser";

--
-- Name: HAS_OPERATION_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph."HAS_OPERATION_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER SEQUENCE production_graph."HAS_OPERATION_id_seq" OWNER TO "postgresUser";

--
-- Name: HAS_OPERATION_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph."HAS_OPERATION_id_seq" OWNED BY production_graph."HAS_OPERATION".id;


--
-- Name: HAS_SEQUENCE; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph."HAS_SEQUENCE" (
)
INHERITS (production_graph._ag_label_edge);


ALTER TABLE production_graph."HAS_SEQUENCE" OWNER TO "postgresUser";

--
-- Name: HAS_SEQUENCE_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph."HAS_SEQUENCE_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER SEQUENCE production_graph."HAS_SEQUENCE_id_seq" OWNER TO "postgresUser";

--
-- Name: HAS_SEQUENCE_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph."HAS_SEQUENCE_id_seq" OWNED BY production_graph."HAS_SEQUENCE".id;


--
-- Name: HAS_STEP; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph."HAS_STEP" (
)
INHERITS (production_graph._ag_label_edge);


ALTER TABLE production_graph."HAS_STEP" OWNER TO "postgresUser";

--
-- Name: HAS_STEP_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph."HAS_STEP_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER SEQUENCE production_graph."HAS_STEP_id_seq" OWNER TO "postgresUser";

--
-- Name: HAS_STEP_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph."HAS_STEP_id_seq" OWNED BY production_graph."HAS_STEP".id;


--
-- Name: _ag_label_vertex; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph._ag_label_vertex (
    id ag_catalog.graphid NOT NULL,
    properties ag_catalog.agtype DEFAULT ag_catalog.agtype_build_map() NOT NULL
);


ALTER TABLE production_graph._ag_label_vertex OWNER TO "postgresUser";

--
-- Name: Inventory; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph."Inventory" (
)
INHERITS (production_graph._ag_label_vertex);


ALTER TABLE production_graph."Inventory" OWNER TO "postgresUser";

--
-- Name: Inventory_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph."Inventory_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER SEQUENCE production_graph."Inventory_id_seq" OWNER TO "postgresUser";

--
-- Name: Inventory_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph."Inventory_id_seq" OWNED BY production_graph."Inventory".id;


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
-- Name: Materials; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph."Materials" (
)
INHERITS (production_graph._ag_label_vertex);


ALTER TABLE production_graph."Materials" OWNER TO "postgresUser";

--
-- Name: Materials_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph."Materials_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER SEQUENCE production_graph."Materials_id_seq" OWNER TO "postgresUser";

--
-- Name: Materials_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph."Materials_id_seq" OWNED BY production_graph."Materials".id;


--
-- Name: NEXT_OPERATION; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph."NEXT_OPERATION" (
)
INHERITS (production_graph._ag_label_edge);


ALTER TABLE production_graph."NEXT_OPERATION" OWNER TO "postgresUser";

--
-- Name: NEXT_OPERATION_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph."NEXT_OPERATION_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER SEQUENCE production_graph."NEXT_OPERATION_id_seq" OWNER TO "postgresUser";

--
-- Name: NEXT_OPERATION_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph."NEXT_OPERATION_id_seq" OWNED BY production_graph."NEXT_OPERATION".id;


--
-- Name: OF_PRODUCT; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph."OF_PRODUCT" (
)
INHERITS (production_graph._ag_label_edge);


ALTER TABLE production_graph."OF_PRODUCT" OWNER TO "postgresUser";

--
-- Name: OF_PRODUCT_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph."OF_PRODUCT_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER SEQUENCE production_graph."OF_PRODUCT_id_seq" OWNER TO "postgresUser";

--
-- Name: OF_PRODUCT_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph."OF_PRODUCT_id_seq" OWNED BY production_graph."OF_PRODUCT".id;


--
-- Name: OpStep; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph."OpStep" (
)
INHERITS (production_graph._ag_label_vertex);


ALTER TABLE production_graph."OpStep" OWNER TO "postgresUser";

--
-- Name: OpStep_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph."OpStep_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER SEQUENCE production_graph."OpStep_id_seq" OWNER TO "postgresUser";

--
-- Name: OpStep_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph."OpStep_id_seq" OWNED BY production_graph."OpStep".id;


--
-- Name: Operation; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph."Operation" (
)
INHERITS (production_graph._ag_label_vertex);


ALTER TABLE production_graph."Operation" OWNER TO "postgresUser";

--
-- Name: Operation_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph."Operation_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER SEQUENCE production_graph."Operation_id_seq" OWNER TO "postgresUser";

--
-- Name: Operation_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph."Operation_id_seq" OWNED BY production_graph."Operation".id;


--
-- Name: Order; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph."Order" (
)
INHERITS (production_graph._ag_label_vertex);


ALTER TABLE production_graph."Order" OWNER TO "postgresUser";

--
-- Name: Order_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph."Order_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER SEQUENCE production_graph."Order_id_seq" OWNER TO "postgresUser";

--
-- Name: Order_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph."Order_id_seq" OWNED BY production_graph."Order".id;


--
-- Name: Product; Type: TABLE; Schema: production_graph; Owner: postgresUser
--

CREATE TABLE production_graph."Product" (
)
INHERITS (production_graph._ag_label_vertex);


ALTER TABLE production_graph."Product" OWNER TO "postgresUser";

--
-- Name: Product_id_seq; Type: SEQUENCE; Schema: production_graph; Owner: postgresUser
--

CREATE SEQUENCE production_graph."Product_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 281474976710655
    CACHE 1;


ALTER SEQUENCE production_graph."Product_id_seq" OWNER TO "postgresUser";

--
-- Name: Product_id_seq; Type: SEQUENCE OWNED BY; Schema: production_graph; Owner: postgresUser
--

ALTER SEQUENCE production_graph."Product_id_seq" OWNED BY production_graph."Product".id;


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
-- Name: inventory; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.inventory (
    item_id integer NOT NULL,
    item_name text NOT NULL,
    quantity integer NOT NULL,
    min_required integer NOT NULL,
    max_capacity integer NOT NULL,
    last_updated timestamp without time zone DEFAULT now(),
    received_at timestamp without time zone DEFAULT now(),
    material_id integer
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
-- Name: materials; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.materials (
    material_id integer NOT NULL,
    material_name text NOT NULL,
    description text
);


ALTER TABLE public.materials OWNER TO "postgresUser";

--
-- Name: materials_material_id_seq; Type: SEQUENCE; Schema: public; Owner: postgresUser
--

CREATE SEQUENCE public.materials_material_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.materials_material_id_seq OWNER TO "postgresUser";

--
-- Name: materials_material_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgresUser
--

ALTER SEQUENCE public.materials_material_id_seq OWNED BY public.materials.material_id;


--
-- Name: operations; Type: TABLE; Schema: public; Owner: postgresUser
--

CREATE TABLE public.operations (
    operation_id integer NOT NULL,
    name text NOT NULL,
    duration integer NOT NULL,
    required_machine_type text NOT NULL,
    material_id integer
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
    quantity integer DEFAULT 0 NOT NULL,
    product_id integer,
    status text DEFAULT 'pending'::text
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
-- Name: CAN_RUN_ON id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."CAN_RUN_ON" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'CAN_RUN_ON'::name))::integer, nextval('production_graph."CAN_RUN_ON_id_seq"'::regclass));


--
-- Name: CAN_RUN_ON properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."CAN_RUN_ON" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: DOES id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."DOES" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'DOES'::name))::integer, nextval('production_graph."DOES_id_seq"'::regclass));


--
-- Name: DOES properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."DOES" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: HAS_OPERATION id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."HAS_OPERATION" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'HAS_OPERATION'::name))::integer, nextval('production_graph."HAS_OPERATION_id_seq"'::regclass));


--
-- Name: HAS_OPERATION properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."HAS_OPERATION" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: HAS_SEQUENCE id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."HAS_SEQUENCE" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'HAS_SEQUENCE'::name))::integer, nextval('production_graph."HAS_SEQUENCE_id_seq"'::regclass));


--
-- Name: HAS_SEQUENCE properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."HAS_SEQUENCE" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: HAS_STEP id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."HAS_STEP" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'HAS_STEP'::name))::integer, nextval('production_graph."HAS_STEP_id_seq"'::regclass));


--
-- Name: HAS_STEP properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."HAS_STEP" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: Inventory id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."Inventory" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'Inventory'::name))::integer, nextval('production_graph."Inventory_id_seq"'::regclass));


--
-- Name: Inventory properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."Inventory" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: Machine id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."Machine" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'Machine'::name))::integer, nextval('production_graph."Machine_id_seq"'::regclass));


--
-- Name: Machine properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."Machine" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: Materials id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."Materials" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'Materials'::name))::integer, nextval('production_graph."Materials_id_seq"'::regclass));


--
-- Name: Materials properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."Materials" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: NEXT_OPERATION id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."NEXT_OPERATION" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'NEXT_OPERATION'::name))::integer, nextval('production_graph."NEXT_OPERATION_id_seq"'::regclass));


--
-- Name: NEXT_OPERATION properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."NEXT_OPERATION" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: OF_PRODUCT id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."OF_PRODUCT" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'OF_PRODUCT'::name))::integer, nextval('production_graph."OF_PRODUCT_id_seq"'::regclass));


--
-- Name: OF_PRODUCT properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."OF_PRODUCT" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: OpStep id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."OpStep" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'OpStep'::name))::integer, nextval('production_graph."OpStep_id_seq"'::regclass));


--
-- Name: OpStep properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."OpStep" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: Operation id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."Operation" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'Operation'::name))::integer, nextval('production_graph."Operation_id_seq"'::regclass));


--
-- Name: Operation properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."Operation" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: Order id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."Order" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'Order'::name))::integer, nextval('production_graph."Order_id_seq"'::regclass));


--
-- Name: Order properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."Order" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: Product id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."Product" ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, 'Product'::name))::integer, nextval('production_graph."Product_id_seq"'::regclass));


--
-- Name: Product properties; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph."Product" ALTER COLUMN properties SET DEFAULT ag_catalog.agtype_build_map();


--
-- Name: _ag_label_edge id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph._ag_label_edge ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, '_ag_label_edge'::name))::integer, nextval('production_graph._ag_label_edge_id_seq'::regclass));


--
-- Name: _ag_label_vertex id; Type: DEFAULT; Schema: production_graph; Owner: postgresUser
--

ALTER TABLE ONLY production_graph._ag_label_vertex ALTER COLUMN id SET DEFAULT ag_catalog._graphid((ag_catalog._label_id('production_graph'::name, '_ag_label_vertex'::name))::integer, nextval('production_graph._ag_label_vertex_id_seq'::regclass));


--
-- Name: inventory item_id; Type: DEFAULT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.inventory ALTER COLUMN item_id SET DEFAULT nextval('public.inventory_item_id_seq'::regclass);


--
-- Name: machines machine_id; Type: DEFAULT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.machines ALTER COLUMN machine_id SET DEFAULT nextval('public.machines_machine_id_seq'::regclass);


--
-- Name: materials material_id; Type: DEFAULT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.materials ALTER COLUMN material_id SET DEFAULT nextval('public.materials_material_id_seq'::regclass);


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
-- Name: materials materials_material_name_key; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_material_name_key UNIQUE (material_name);


--
-- Name: materials materials_pkey; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_pkey PRIMARY KEY (material_id);


--
-- Name: operations operations_name_unique; Type: CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.operations
    ADD CONSTRAINT operations_name_unique UNIQUE (name);


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
-- Name: inventory inventory_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(material_id);


--
-- Name: operations operations_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgresUser
--

ALTER TABLE ONLY public.operations
    ADD CONSTRAINT operations_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(material_id);


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

\unrestrict Iew6i0lVkMfUea3PqtFAULTv4OGpGcd6b6YoVMPIaNlhz9yVVacffhYCXoO4lNr

