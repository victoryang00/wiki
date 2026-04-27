## Lazy Evaluation in C艹

C++ `view` is interesting because it makes a pipeline visible without forcing the data to move yet. That sounds like a language feature, but for systems work it is really a scheduling feature: delay the materialization point until you know where the data should live.

The classic example is:

```cpp
auto xs = input
        | std::views::filter(is_hot)
        | std::views::transform(to_work_item)
        | std::views::take(batch_size);
```

No new container is required for the intermediate steps. The program describes a traversal. The actual memory traffic happens when a consumer pulls from the view.

## Why I care

For CXL, GPU staging, and computational storage, the bad version of a pipeline is:

1. read remote data;
2. copy into a host buffer;
3. transform;
4. copy into a device buffer;
5. finally execute.

The better version is to preserve the pipeline as long as possible, then fuse the traversal at the boundary where execution actually happens. A view-like interface is a good software shape for that idea.

## Where views are sharp

- Lifetime: a view can outlive the object it references if the code is careless.
- Hidden complexity: lazy code can hide repeated traversal.
- Debugging: the object you see in the debugger is a recipe, not the data.

My rule: use views when they make movement and ownership clearer. If they only make the code look clever, materialize the container and move on.
