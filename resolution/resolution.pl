:- use_module(library(readutil)).

neg(neg(L), L) :- !.
neg(L, neg(L)).

is_tautology(C) :-
    member(L, C),
    neg(L, NL), 
    member(L2, C),
    L2 == NL,
    !.

subsumes(General, Specific) :-
    copy_term(General, G),
    forall(
        member(L, G),
        member(L, Specific)
    ).

normalize(C, N) :- sort(C, N).

rename_var(C, R) :- copy_term(C, R).

resolve(C1, C2, Resolvent) :-
    rename_var(C1, R1),
    rename_var(C2, R2),
    select(L1, R1, Rest1),
    neg(L1, NL1),
    select(L2, R2, Rest2),
    unify_with_occurs_check(NL1, L2),
    append(Rest1, Rest2, Temp),
    normalize(Temp, Resolvent),
    \+ is_tautology(Resolvent).

all_resolvents(Clauses, Resolvents) :-
    findall(
        R, 
        (
            member(C1, Clauses), 
            member(C2, Clauses),
            C1 \== C2, 
            resolve(C1, C2, R)
        ),
        All
    ),
    sort(All, Resolvents).

new_resolvents(Clauses, New) :-
    all_resolvents(Clauses, All),
    include(is_good_resolvent(Clauses), All, New).

is_good_resolvent(Clauses, R) :-
    \+ member(R, Clauses),
    \+ is_subsumed_by_any(R, Clauses).

is_subsumed_by_any(C, Clauses) :-
    member(C2, Clauses), 
    C2 \== C, 
    subsumes(C2, C),
    !.

saturate(Clauses, Result) :-
    ( 
        member([], Clauses) ->
        Result = unsatisfiable ;
        new_resolvents(Clauses, New),
        ( 
            New = [] ->
            Result = satisfiable ; 
                member([], New) ->
                Result = unsatisfiable ;
                append(Clauses, New, Extended),
                list_to_set(Extended, Next),
                saturate(Next, Result)
        )
    ).

resolution(Clauses, Result) :-
    maplist(normalize, Clauses, Norm),
    exclude(is_tautology, Norm, NoTaut),
    list_to_set(NoTaut, Init),
    ( 
        member([], Init) -> 
        Result = unsatisfiable ; 
        saturate(Init, Result) 
    ).

% % % % % % % % % % % % % 
read_kb_from_file(FileName, Clauses) :-
    open(FileName, read, Stream),
    read_clauses_from_stream(Stream, Clauses),
    close(Stream).

read_clauses_from_stream(Stream, []) :-
    at_end_of_stream(Stream), !.

read_clauses_from_stream(Stream, [Clause|Rest]) :-
    \+ at_end_of_stream(Stream),
    read_term(Stream, Clause, []),
    Clause \= end_of_file,
    read_clauses_from_stream(Stream, Rest).

run_resolution_file(FileName, Result) :-
    read_kb_from_file(FileName, Clauses),
    resolution(Clauses, Result).