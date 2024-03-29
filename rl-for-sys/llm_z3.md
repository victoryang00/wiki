# LLM for Code Generation
Need logic guided learning for code generation. Recent LLM works have put more focus on ground truth-oriented code generation, which also helps the code repairing and debugging. LLMs have demonstrated state-of-the-art performance in code synthesis. Primary applications involve structured communication with computer systems, like creating programs from natural language descriptions, assisting with code completion, debugging, and producing documentation.

## SoTA use of LLM
Normally, people fine-tune models either with a better dataset from Google Search and Youtube’s user browsing history that Google’s Gemini[21] trained with, the GitHub codebase that Github Copilot by Microsoft trained with, or Stack Overflow answers that OpenAI’s ChatGPT trained with, or a better transformer layer that memorizes more context, which for reaching the goal, researchers typically add more layer depths, speculative decoding or token compression. There are other ways, like RWKV, that reuse the neural network of RNN with inference memory hardened, which is easily deployed in edge endpoints but is still not production ready. 
## LLM for logic proof
LLM logic proof, like LogicGuide in  is useful for getting correct semantics that is self-provable. It takes the underlying logic for every logic unit, which could be "if", "despite", or "because". The auto-generated logic, the evaluateable sequence, will be fed into the logic solver, and the final result complies with the logic's result. Or like Optimizer in  uses LLM itself to instill the logic does not make the direction to the correction. Because it's unlike Alpha-Zero, the last self-competing training will converge to the true results anyway with the remaining exploration winning metrics. In the logic-proof space, there's no foundation for the reward function easily written. These approaches neither make a mapping to the code logic nor have an automatically re-prompting mechanism.

## LLM for neural fuzzing
The LLM for neural fuzzing is a new type of code semantic understanding; we think the coverage-based method is legacy since the LLM should know the context if we optimize for this metric; it will be in trouble not getting the real work done because LLM can internally know the job and does not generate well-grounded-truth-guided code.

# Z3 for Verification
I think the Z3 is a good tool for verification. LLM can know the stable mapping from natural language to z3 language for learning new things. However, the reasoning ability of LLM tools is an open problem. We still couldn’t say with no prior knowledge or similar questions before; it can provide a logical prompt. During the training, since the code generation maintains the logic preserving property, Code LLAMA will utilize every instruction logic point done by infilling, understanding the long context, and codegen the best choice based on Reinforcement learning from fine-tuned human feedback(RLHF), this feedback can be programmer’s alignment, not necessarily the general public’s alignment. Feedback based on this feedback will store the previous context to maintain the code’s correctness.The problem with this is the RLHF is only maintaining the correctness mapping for the function code generation but not the exact semantic mapping for each sentence and corresponding functions’ state, even with the best feedback. Thus, we need extra information with the kernel, and re-prompt the LLM for rethinking the context and codegen the corresponding functions’ state.
1. good to map the compiler for LLM to understand
2. Is there a way of Reinforcement Learning with compiler groud-truth guided.
3. The compiling and verification leaks information that is sound for LLM to learn.

## Z3 for Logic Proof
LLM for auto code logic proof has other implementations for C code applying CMBC or other formal verification during training and prompting. eBPF is a more domain-specific way of proving stable mapping from the underlying logic.

## Reference
1. KEN: Kernel Extensions using Natural Language