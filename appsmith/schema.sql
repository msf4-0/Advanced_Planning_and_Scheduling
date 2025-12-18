--
-- PostgreSQL database dump
--

\restrict zh5mb8WgFbzAvC0KvJgfe7iiEfk3bY24EPD2XbCqdyGQf45PAfuPX5RoWmmghrm

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


ALTER TABLE public.inventory_item_id_seq OWNER TO "postgresUser";

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


ALTER TABLE public.machines_machine_id_seq OWNER TO "postgresUser";

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


ALTER TABLE public.operations_operation_id_seq OWNER TO "postgresUser";

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


ALTER TABLE public.orders_order_id_seq OWNER TO "postgresUser";

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


ALTER TABLE public.product_operations_view OWNER TO "postgresUser";

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


ALTER TABLE public.products_product_id_seq OWNER TO "postgresUser";

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


ALTER TABLE public.schedule_archive_archive_id_seq OWNER TO "postgresUser";

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


ALTER TABLE public.schedule_results_schedule_id_seq OWNER TO "postgresUser";

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

\unrestrict zh5mb8WgFbzAvC0KvJgfe7iiEfk3bY24EPD2XbCqdyGQf45PAfuPX5RoWmmghrm

